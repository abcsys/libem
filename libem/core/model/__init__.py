from libem.core.model import (
    openai, llama
)
from libem.core.util import run_async_task


def call(*args, **kwargs) -> dict:
    return run_async_task(
        async_call(*args, **kwargs)
    )


async def async_call(*args, **kwargs) -> dict:
    if kwargs.get("model", "") == "llama3":
        return llama.call(*args, **kwargs)
    else:
        return await openai.async_call(*args, **kwargs)
