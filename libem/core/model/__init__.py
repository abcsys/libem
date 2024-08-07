from libem.core.model import (
    openai, llama
)
from libem.core import exec
import libem

def call(*args, **kwargs) -> dict:
    return exec.run_async_task(
        async_call(*args, **kwargs)
    )


async def async_call(*args, **kwargs) -> dict:
    if kwargs.get("model", "") == "llama3":
        return llama.call(*args, **kwargs)
    elif kwargs.get("model", "") == "llama3.1":
        libem.calibrate({
            "libem.match.prompt.output": "Do not provide explanation. Please only give your answer in the form of a single ‘yes’ or ‘no’.",
        }, verbose=True)
        return llama.call(*args, **kwargs)
    else:
        return await openai.async_call(*args, **kwargs)


def reset():
    openai.reset()
    llama.reset()
