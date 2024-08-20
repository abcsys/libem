import os
import json
import httpx
import importlib
import inspect

from anthropic import (
    AsyncAnthropic, APITimeoutError
)

import libem
from libem.core import exec

os.environ.setdefault(
    "CLAUDE_API_KEY",
    libem.LIBEM_CONFIG.get("CLAUDE_API_KEY", "")
)

_client = None


def get_client():
    global _client

    if not os.environ.get("CLAUDE_API_KEY"):
        raise EnvironmentError(f"CLAUDE_API_KEY is not set.")

    if not _client:
        _client = AsyncAnthropic(
            api_key=os.environ["CLAUDE_API_KEY"],
            http_client=httpx.AsyncClient(
                limits=httpx.Limits(
                    max_connections=1000,
                    max_keepalive_connections=100
                )
            )
        )
    return _client


def call(*args, **kwargs) -> dict:
    return exec.run_async_task(
        async_call(*args, **kwargs)
    )


# Model call with multiple rounds of tool use
async def async_call(
        prompt: str | list | dict,
        tools: list[str] = None,
        context: list = None,
        model: str = "claude-3-5-sonnet-20240620",
        temperature: float = 0.0,
        seed: int = None,
        max_model_call: int = 3,
) -> dict:
    client = get_client()

    context = context or []

    # format the prompt to messages
    system_message = None
    user_messages = []

    match prompt:
        case list():
            for msg in prompt:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
        case dict():
            for role, content in prompt.items():
                if role == "system":
                    system_message = content
                else:
                    user_messages.append({"role": role, "content": content})
        case str():
            user_messages = [{"role": "user", "content": prompt}]
        case _:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")

    # Handle context
    for msg in context:
        if msg["role"] == "system":
            if system_message is None:
                system_message = msg["content"]
            else:
                system_message += "\n" + msg["content"]
        else:
            user_messages.insert(0, msg)

    messages = user_messages

    # trace variables
    num_model_calls = 0
    num_input_tokens, num_output_tokens = 0, 0
    tool_usages, tool_outputs = [], []

    """Start call"""

    if not tools:
        try:
            response = await client.messages.create(
                messages=messages,
                system=system_message,
                model=model,
                temperature=temperature,
                max_tokens = 1000,
            )
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)
        
        response_message = response.content[0].text
        print(response_message)
        num_model_calls += 1
        num_input_tokens += response.usage.input_tokens
        num_output_tokens += response.usage.input_tokens
    else:
        # Load the tool modules
        tools = [importlib.import_module(tool) for tool in tools]

        # Get the functions from the tools and
        # prefer async functions if available
        available_functions = {
            tool.name: getattr(tool, 'async_func', tool.func)
            for tool in tools
        }

        # Get the schema from the tools
        tools = [tool.schema for tool in tools]

        # Call model
        try:
            response = await client.messages.create(
                messages=messages,
                system=system_message,
                tools=tools,
                tool_choice="auto",
                model=model,
                temperature=temperature,
                max_tokens = 1000,
            )
            
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)

        response_message = response.content[0].text
        tool_uses = response_message.tool_use
        
        num_model_calls += 1
        num_input_tokens += response.usage.input_tokens
        num_output_tokens += response.usage.input_tokens

        # Call tools
        while tool_use:
            messages.append(response_message)

            for tool_use in tool_uses:
                function_name = tool_use.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_use.input)

                libem.debug(f"[{function_name}] {function_args}")

                if inspect.iscoroutinefunction(function_to_call):
                    function_response = function_to_call(**function_args)
                else:
                    function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                        "tool_use_id": tool_use.id,
                    }
                )

                tool_usages.append({
                    "id": tool_use.id,
                    'name': function_name,
                    "arguments": function_args,
                    "response": function_response,
                })

                tool_outputs.append({
                    function_name: function_response,
                })

            tool_uses = []

            if num_model_calls < max_model_call:
                # Call the model again with the tool outcomes
                try:
                    response = await client.messages.create(
                        messages=messages,
                        system=system_message,
                        tools=tools,
                        tool_choice="auto",
                        model=model,
                        temperature=temperature,
                        max_tokens = 1000,
                    )
                except APITimeoutError as e:  # catch timeout error
                    raise libem.ModelTimedoutException(e)

                response_message = response.content[0].text
                tool_uses = response_message.tool_use
                
                num_model_calls += 1
                num_input_tokens += response.usage.input_tokens
                num_output_tokens += response.usage.input_tokens

            if num_model_calls == max_model_call:
                libem.debug(f"[model] max call reached: "
                            f"{messages}\n{response_message}")

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
        "output": response_message,
        "tool_outputs": tool_outputs,
        "messages": messages,
        "stats": {
            "num_model_calls": num_model_calls,
            "num_input_tokens": num_input_tokens,
            "num_output_tokens": num_output_tokens,
        }
    }


def reset():
    global _client
    _client = None