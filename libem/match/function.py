import time
import asyncio
from pprint import pformat
from typing import Any

import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
from libem.core import struct
from libem.core import model
from libem.core.util import throttled_async_run_all

schema = {
    "type": "function",
    "function": {
        "name": "match",
        "description": "Perform entity matching given a pair or two lists of entity descriptions.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "string",
                    "description": "Description of the first entity.",
                },
                "right": {
                    "type": "string",
                    "description": "Description of the second entity.",
                },
            },
            "required": ["left", "right"],
        },
    }
}

def func(left: Any | list[Any], 
         right: Any | list[Any]) -> Any | list[Any]:

    return asyncio.run(async_func(left, right))

async def async_func(left: Any | list[Any], 
         right: Any | list[Any]) -> Any | list[Any]:
      
    if type(left) is list and type(right) is list:
        assert len(left) == len(right)
        result = await throttled_async_run_all([
                    match(left[i], right[i], i) 
                    for i in range(len(left))])
    else:
        result = await match(left, right)

    return result


async def match(left: Any, right: Any, id: int = 0) -> dict:
    start = time.time()

    system_prompt = Prompt.join(
        prompt.role(),
        prompt.rules(),
        prompt.experiences(),
        struct.CoT() if parameter.cot() else "",
        struct.Confidence() if parameter.confidence() else "",
        prompt.output(),
    )

    match_prompt = Prompt.join(
        prompt.query(
            left=left,
            right=right
        ),
    )

    shots: list[dict] = prompt.shots()

    _prompt = [
        {"role": "system", "content": system_prompt},
        *shots,
        {"role": "user", "content": match_prompt},
    ]

    model_output = await model.call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )

    libem.debug(f"[match] prompt:\n"
                f"{pformat(_prompt, sort_dicts=False)}\n"
                f"[match] model output:\n"
                f"{model_output['output']}")

    output = parse_output(model_output["output"])

    libem.trace.add({"match": {"id": id,
                               "left": left, "right": right,
                               "prompt": _prompt,
                               "model_output": model_output,
                               "result": output,
                               "latency": time.time() - start}})
    return output


def parse_output(output: str) -> dict:
    """Handle the model output of format:
    ```
    <explanation> (e.g., "Name Comparison: ...")
    <confidence> (e.g., "Confidence Score: 5" or "5")
    <answer> (e.g., yes)
    ```
    """
    output = output.split("\n")[::-1]

    answer = output.pop(0).lower()
    answer = "yes" if "yes" in answer else "no"

    confidence, explanation = None, None

    if parameter.confidence():
        for i, line in enumerate(output):
            line = line.lower()
            if 'confidence score' in line or str.isdigit(line):
                confidence = ''.join(filter(str.isdigit, line))
                confidence = int(confidence)
                output = output[i + 1:]
                break

    if parameter.cot():
        explanation = "\n".join(output[::-1])

    return {
        "answer": answer,
        "confidence": confidence,
        "explanation": explanation,
    }
