import os
import json
import importlib

from openai import OpenAI, APITimeoutError

import libem


def call(*args, **kwargs) -> str:
    return openai(*args, **kwargs)


""" OpenAI """

os.environ.setdefault(
    "OPENAI_API_KEY",
    libem.LIBEM_CONFIG.get("OPENAI_API_KEY", "")
)


# LLM call with multiple rounds of tool use
def openai(prompt: str, tools: list[str],
           model: str, temperature: float,
           max_model_call: int = 3,
           seed: int = None) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(f"OPENAI_API_KEY is not set. "
                               f"Check your environment or {libem.LIBEM_CONFIG_FILE}.")
    client = OpenAI()
    num_model_call, tokens = 0, 0

    if len(tools) == 0:
        """ Call with no tool use """
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                seed=seed,
                temperature=temperature,
            )
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)

        response_message = response.choices[0].message
        tokens += response.usage.total_tokens

    else:
        """ Call with tools """
        # Load the tool modules
        tools = [importlib.import_module(tool) for tool in tools]

        # Get the functions from the tools
        available_functions = {
            tool.name: tool.func for tool in tools
        }
        # Get the schema from the tools
        tools = [tool.schema for tool in tools]

        # Call the model
        messages = [{"role": "user", "content": prompt}]
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                seed=seed,
                temperature=temperature,
            )
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)

        response_message = response.choices[0].message
        tokens += response.usage.total_tokens
        tool_calls = response_message.tool_calls

        # Call the tools
        num_model_call = 1
        while tool_calls and num_model_call < max_model_call:
            messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                libem.info(f"Tool: {function_name} - running ..")
                function_response = function_to_call(**function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                libem.trace.add({
                    'tool': {
                        "id": tool_call.id,
                        'name': function_name,
                        "arguments": function_args,
                        "response": function_response
                    }
                })
                libem.info(f"Tool: {function_name} - {function_response}")

            # Call the model again with the tool outcomes
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    seed=seed,
                    temperature=temperature,
                )
            except APITimeoutError as e:  # catch timeout error
                raise libem.ModelTimedoutException(e)

            response_message = response.choices[0].message
            tokens += response.usage.total_tokens
            tool_calls = response_message.tool_calls
            num_model_call += 1

        if num_model_call == max_model_call:
            libem.warn(f"Max call reached: {messages}\n{response_message}")

    # add model calls to trace
    libem.trace.add({
        'model': {
            'num_calls': num_model_call,
            'tokens': tokens
        }
    })

    return response_message.content
