from libem.core.model import (
    openai, llama, claude
)
from libem.core import exec

def output_schema(*args, **kwargs) -> dict:
    return openai.output_schema(*args, **kwargs)

def call(*args, **kwargs) -> dict:
    return exec.run_async_task(
        async_call(*args, **kwargs)
    )


async def async_call(*args, **kwargs) -> dict:
    match kwargs.get("model", ""):
        case "llama3" | "llama3.1" | "llama3.2-3b" | "llama3.2-1b":
            return llama.call(*args, **kwargs)
        case "claude-3-5-sonnet-20240620":
            return await claude.call(*args, **kwargs)
        case _:
            return await openai.async_call(*args, **kwargs)


def reset():
    openai.reset()
    claude.reset()
    llama.reset()
