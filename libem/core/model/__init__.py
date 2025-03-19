from typing import Any
from libem.core.model import (
    openai, llama, claude, gemini
)
from libem.core import exec


def format_text(*args, **kwargs) -> dict:
    return openai.format_text(*args, **kwargs)


def format_image(*args, **kwargs) -> dict:
    return openai.format_image(*args, **kwargs)


def output_schema(*args, **kwargs) -> Any:
    return openai.output_schema(*args, **kwargs)


def call(*args, **kwargs) -> dict:
    return exec.run_async_task(
        async_call(*args, **kwargs)
    )


async def async_call(*args, **kwargs) -> dict:
    model = kwargs.get("model", "")
    match model:
        case "llama3" | "llama3.1" | "llama3.2-3b" | "llama3.2-1b":
            return llama.call(*args, **kwargs)
        case "claude-3-5-sonnet-20240620":
            return await claude.async_call(*args, **kwargs)
        case _ if model in gemini.MODELS:
            return await gemini.async_call(*args, **kwargs)
        case _:
            return await openai.async_call(*args, **kwargs)


def reset():
    openai.reset()
    claude.reset()
    llama.reset()
    gemini.reset()
