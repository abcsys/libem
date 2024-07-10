import asyncio
import inspect
import os
import json
import httpx
import importlib

from openai import AsyncOpenAI, APITimeoutError

import libem


def call(*args, **kwargs) -> dict:
    return openai(*args, **kwargs)

async def async_call(*args, **kwargs) -> dict:
    return await async_openai(*args, **kwargs)

""" OpenAI """

# use a single openai client to avoid memory leak
openai_client = None

# LLM call with multiple rounds of tool use
def openai(*args, **kwargs) -> dict:
    return asyncio.run(async_openai(*args, **kwargs))

async def async_openai(prompt: str | list | dict,
           tools: list[str] = None,
           context: list = None,
           model: str = "gpt-4o",
           temperature: float = 0.0,
           seed: int = None,
           max_model_call: int = 3,
           ) -> dict:
    
    # retrieve api key and set up openai client
    global openai_client
    
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ.setdefault(
            "OPENAI_API_KEY",
            libem.LIBEM_CONFIG.get("OPENAI_API_KEY", "")
        )
    
    if not openai_client:
        # set limits to prevent too many connections error
        openai_client = AsyncOpenAI(
            http_client=httpx.AsyncClient(
                limits=httpx.Limits(
                    max_connections=1000,
                    max_keepalive_connections=100
                )
            )
        )

    # format the prompt to messages
    match prompt:
        case list():
            messages = prompt
        case dict():
            messages = []
            for role, content in prompt.items():
                if content:
                    messages.append({"role": role, "content": content})
        case str():
            messages = [{"role": "user", "content": prompt}]
        case _:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")

    context = context or []
    messages = context + messages

    # trace variables
    num_model_calls = 0
    num_input_tokens, num_output_tokens = 0, 0
    tool_usages, tool_outputs = [], []

    """Start call"""

    if not tools:
        try:
            response = await openai_client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                seed=seed,
            )
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)

        response_message = response.choices[0].message

        num_model_calls += 1
        num_input_tokens += response.usage.total_tokens - response.usage.completion_tokens
        num_output_tokens += response.usage.completion_tokens
    else:
        # Load the tool modules
        tools = [importlib.import_module(tool) for tool in tools]

        # Get the functions from the tools
        available_functions = {
            tool.name: tool.async_func 
                       if 'async_func' in dir(tool) else tool.func 
                       for tool in tools
        }
        # Get the schema from the tools
        tools = [tool.schema for tool in tools]

        # Call model
        try:
            response = await openai_client.chat.completions.create(
                messages=messages,
                tools=tools,
                tool_choice="auto",
                model=model,
                temperature=temperature,
                seed=seed,
            )
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        num_model_calls += 1
        num_input_tokens += response.usage.total_tokens - response.usage.completion_tokens
        num_output_tokens += response.usage.completion_tokens

        # Call tools
        while tool_calls:
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                libem.debug(f"[{function_name}] {function_args}")

                # await if tool is async
                if inspect.iscoroutinefunction(function_to_call):
                    function_response = await function_to_call(**function_args)
                else:
                    function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                        "tool_call_id": tool_call.id,
                    }
                )

                tool_usages.append({
                    "id": tool_call.id,
                    'name': function_name,
                    "arguments": function_args,
                    "response": function_response,
                })

                tool_outputs.append({
                    function_name: function_response,
                })

            tool_calls = []

            if num_model_calls < max_model_call:
                # Call the model again with the tool outcomes
                try:
                    response = await openai_client.chat.completions.create(
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        model=model,
                        temperature=temperature,
                        seed=seed,
                    )
                except APITimeoutError as e:  # catch timeout error
                    raise libem.ModelTimedoutException(e)

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                num_model_calls += 1
                num_input_tokens += response.usage.total_tokens - response.usage.completion_tokens
                num_output_tokens += response.usage.completion_tokens

            if num_model_calls == max_model_call:
                libem.debug(f"[model] max call reached: {messages}\n{response_message}")

    """End call"""

    messages.append(response_message)

    libem.trace.add({
        "model": {
            "messages": messages,
            "tool_usages": tool_usages,
            "num_model_calls": num_model_calls,
            "num_input_tokens": num_input_tokens,
            "num_output_tokens": num_output_tokens,
        }
    })

    return {
        "output": response_message.content,
        "tool_outputs": tool_outputs,
        "messages": messages,
        "stats": {
            "num_model_calls": num_model_calls,
            "num_input_tokens": num_input_tokens,
            "num_output_tokens": num_output_tokens,
        }
    }
