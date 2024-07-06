import os
import json
import importlib

from openai import OpenAI, APITimeoutError

import libem


def call(*args, **kwargs) -> dict:
    return openai(*args, **kwargs)


""" OpenAI """

os.environ.setdefault(
    "OPENAI_API_KEY",
    libem.LIBEM_CONFIG.get("OPENAI_API_KEY", "")
)


# LLM call with multiple rounds of tool use
def openai(prompt: str | list | dict,
           tools: list[str] = None,
           context: list = None,
           model: str = "gpt-4o",
           temperature: float = 0.0,
           seed: int = None,
           max_model_call: int = 3,
           ) -> dict:
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(f"OPENAI_API_KEY is not set.")

    client = OpenAI()

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
            response = client.chat.completions.create(
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
            tool.name: tool.func for tool in tools
        }
        # Get the schema from the tools
        tools = [tool.schema for tool in tools]

        # Call model
        try:
            response = client.chat.completions.create(
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
                    response = client.chat.completions.create(
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
