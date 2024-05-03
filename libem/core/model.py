import os
import json
import types

from openai import OpenAI

from libem.constant import LIBEM_CONFIG

""" OpenAI calls """
os.environ["OPENAI_API_KEY"] = LIBEM_CONFIG.get("openai_api_key", "")


# LLM call with multiple rounds of tool use
def run(prompt: str, model: str, tools: list[types.ModuleType],
        max_call: int = 3) -> str:
    assert os.environ.get("OPENAI_API_KEY", "") != "", \
        "OPENAI_API_KEY is not set, you can set it in the environment or in the config file"
    client = OpenAI()

    # Get the functions from the tools
    available_functions = {
        tool.func.__name__: tool.func for tool in tools
    }
    # Get the schema from the tools
    tools = [tool.schema for tool in tools]

    # Call the model
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Call the tools
    num_call = 1
    while tool_calls and num_call < max_call:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        # Call the model again with the tool outcomes
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
    if num_call == max_call:
        raise Warning(f"Max call reached: {messages}\n{response_message}")
    return response_message
