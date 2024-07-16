import os
import json
import time
import httpx
import platform
import importlib

from openai import (
    AsyncOpenAI, APITimeoutError
)

import libem
from libem.core.util import run_async_task


def call(*args, **kwargs) -> dict:
    return run_async_task(
        async_call(*args, **kwargs)
    )


async def async_call(*args, **kwargs) -> dict:
    if kwargs.get("model", "") == "llama3":
        return llama(*args, **kwargs)
    else:
        return await async_openai(*args, **kwargs)


""" OpenAI """

os.environ.setdefault(
    "OPENAI_API_KEY",
    libem.LIBEM_CONFIG.get("OPENAI_API_KEY", "")
)

_openai_client = None


def get_openai_client():
    global _openai_client

    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(f"OPENAI_API_KEY is not set.")

    if not _openai_client:
        _openai_client = AsyncOpenAI(
            http_client=httpx.AsyncClient(
                limits=httpx.Limits(
                    max_connections=1000,
                    max_keepalive_connections=100
                )
            )
        )
    return _openai_client


def openai(*args, **kwargs) -> dict:
    return run_async_task(
        async_openai(*args, **kwargs)
    )


# Model call with multiple rounds of tool use
async def async_openai(
        prompt: str | list | dict,
        tools: list[str] = None,
        context: list = None,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        seed: int = None,
        max_model_call: int = 3,
) -> dict:
    client = get_openai_client()

    context = context or []

    # format the prompt to messages
    match prompt:
        case list():
            messages = prompt
        case dict():
            messages = [{
                "role": role,
                "content": content
            } for role, content in prompt.items()]
        case str():
            messages = [{"role": "user", "content": prompt}]
        case _:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")

    messages = context + messages

    # trace variables
    num_model_calls = 0
    num_input_tokens, num_output_tokens = 0, 0
    tool_usages, tool_outputs = [], []

    """Start call"""

    if not tools:
        try:
            response = await client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                seed=seed,
            )
        except APITimeoutError as e:  # catch timeout error
            raise libem.ModelTimedoutException(e)

        response_message = response.choices[0].message

        num_model_calls += 1
        num_input_tokens += response.usage.total_tokens - \
                            response.usage.completion_tokens
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
            response = await client.chat.completions.create(
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
        num_input_tokens += response.usage.total_tokens - \
                            response.usage.completion_tokens
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
                    response = await client.chat.completions.create(
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


_llama_model, _llama_tokenizer = None, None

""" Llama """


def llama(prompt: str | list | dict,
          tools: list[str] = None,
          context: list = None,
          model: str = "llama3",
          temperature: float = 0.0,
          seed: int = None,
          max_model_call: int = 3,
          ) -> dict:
    global _llama_model, _llama_tokenizer

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

    BOS = "<|begin_of_text|>"
    SYS = "<|start_header_id|>system<|end_header_id|>"
    USER = "<|start_header_id|>user<|end_header_id|>"
    ASSIS = "<|start_header_id|>assistant<|end_header_id|>"
    EOS = "<|eot_id|>"

    input_text = BOS
    for message in messages:
        if message['role'] == 'system':
            input_text = input_text + SYS + message['content'] + EOS
        elif message['role'] == 'user':
            input_text = input_text + USER + message['content'] + EOS
    input_text = input_text + ASSIS

    context = context or []
    messages = context + [input_text]

    # apple silicon
    if platform.machine() == "arm64" and platform.system() == "Darwin":
        # Load the model using MLX for apple silicon device
        if model == "llama3":
            # first check whether mlx_lm is installed
            try:
                from mlx_lm import load, generate
            except ImportError:
                raise ImportError("mlx_lm is not installed.")
            model_path = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
        else:
            raise ValueError(f"{model} is not supported.")

        if _llama_model is None or _llama_tokenizer is None:
            start = time.time()
            _llama_model, _llama_tokenizer = load(model_path)
            libem.debug(f"model loaded in {time.time() - start:.2f} seconds.")
        else:
            libem.debug("model loaded from cache")
        model, tokenizer = _llama_model, _llama_tokenizer

        if tools:
            raise libem.ToolUseUnsupported("Tool use is not supported")

        response = generate(model, tokenizer, prompt=messages[0], temp=temperature)
    else:
        raise ValueError(f"{platform.machine()} {platform.system()} is not supported.")

    return {
        "output": response,
        "messages": "messages is not supported",
        "tool_outputs": "Tool output is not supported",
        "stats": {
            "num_model_calls": 1,
            "num_input_tokens": -1,
            "num_output_tokens": -1,
        }
    }


def reset():
    global _openai_client
    _openai_client = None
    _llama_model = None
    _llama_tokenizer = None
