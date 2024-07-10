import re
import time
import asyncio
import hashlib
from pprint import pformat
from typing import Any

import libem
from libem.match import prompt, parameter
from libem.core import struct
from libem.core import model
from libem.core.struct import Prompt
from libem.core.util import throttled_async_run_all

schema = {
    "type": "function",
    "function": {
        "name": "match",
        "description": "Perform entity matching given two entity descriptions.",
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
         right: Any | list[Any]) -> dict | list[dict]:
    return asyncio.run(async_func(left, right))

async def async_func(left: Any | list[Any], 
                     right: Any | list[Any]) -> dict | list[dict]:
    assert type(left) == type(right)

    if parameter.batch_size() > 1:
        return await batch(left, right)
    else:
        if type(left) is list:
            return await individual(left, right)
        else:
            return await once(left, right)
    

async def once(left: str, right: str) -> dict:
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

    response = await model.async_call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )

    libem.debug(f"[match] prompt:\n"
                f"{pformat(_prompt, sort_dicts=False)}\n"
                f"[match] model output:\n"
                f"{response['output']}")

    output = parse_output(response["output"])

    libem.trace.add({
        "match": {
            "left": left, "right": right,
            "output": output,
            "prompt": _prompt,
            "model_output": response["output"],
            "tool_outputs": response["tool_outputs"],
            "model_usage": response["stats"],
            "latency": time.time() - start,
        }
    })

    return output


async def individual(left: list, right: list) -> list[dict]:
    return await throttled_async_run_all(
        once(l, r)
        for l, r in zip(left, right)
    )


async def batch(left: list, right: list) -> list[dict]:
    assert len(left) == len(right)
    
    if len(left) <= parameter.batch_size():
        return await _proc_batch(left, right)
    else:
        batches = _create_batches(left, right)
    
        results = await throttled_async_run_all(
            _proc_batch(l, r)
            for l, r in batches
        )
        
        # flatten results list
        output = []
        for r in results:
            output.extend(r)
        
        return output


def _create_batches(left: list, right: list) -> list:
    num_pairs = len(left)
    batch_size = parameter.batch_size()
    batch_start = 0
    batches = []

    # generate left and right batches
    while batch_start < num_pairs:
        batch_end = min(batch_start + batch_size, num_pairs)
        
        batches.append((left[batch_start:batch_end], right[batch_start:batch_end]))

        batch_start += batch_size

    return batches


async def _proc_batch(left: list, right: list) -> list[dict]:
    start = time.time()

    output, size = [], len(left)
    digests = []

    digests.append([
        digest(l, r)
        for l, r in zip(left, right)
    ])

    system_prompt = Prompt.join(
        prompt.role(),
        prompt.rules(),
        prompt.experiences(),
        prompt.output(),
    )

    shots: list[dict] = prompt.shots()

    match_prompt = Prompt.join(*[
        Prompt.join(
            f"Q{i + 1}:",
            prompt.query(
                left=l,
                right=r
            )
        )
        for i, l, r in zip(
            range(size), left, right
        )])

    _prompt = [
        {"role": "system", "content": system_prompt},
        *shots,
        {"role": "user", "content": match_prompt},
    ]

    response = await model.async_call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )

    output_lines = response["output"].split('\n')

    # parsing model output for each pair
    # assuming model output is in the format:
    # Q1: <answer>
    # Q2: <answer>
    # ...
    # Qn: <answer>
    # where each <answer> may contain multiple lines.
    if re.match(r"^Q\d+:", output_lines[0]):
        answer_lines = []

        for line in output_lines:
            if re.match(r"^Q\d+:", line):
                # parse the previous answer
                if len(answer_lines) > 0:
                    output.append(
                        parse_output('\n'.join(answer_lines))
                    )
                # reset answer lines
                answer_lines = [line]
            else:
                answer_lines.append(line)

        # parse the last answer
        if len(answer_lines) > 0:
            output.append(
                parse_output('\n'.join(answer_lines))
            )
        
        # if number of answers are greater than number of inputs,
        # only return the first len(inputs) answers.
        # This can happen if the model does not follow the expected format.
        if len(output) > size:
            output = output[0:size]
    else:
        # if the model output does not follow the expected
        # format, assume all answers are the same
        answer = parse_output(response["output"])
        output = [answer for _ in range(size)]

    libem.debug(f"[match] batch output:\n"
                f"{response['output']}")

    libem.trace.add({
        "match": {
            "left": left, "right": right,
            "output": output,
            "prompt": _prompt,
            "model_output": response["output"],
            "tool_outputs": response["tool_outputs"],
            "model_usage": response["stats"],
            "latency": time.time() - start,
        }
    })

    return output


def digest(left, right) -> str:
    return hashlib.md5(
        f"{left} {right}".encode()
    ).hexdigest()


def parse_output(output: str) -> dict:
    """Handle the model output of format:
    ```
    <explanation> (e.g., "Name Comparison: ...")
    <confidence> (e.g., "Confidence Score: 5" or "5")
    <answer> (e.g., yes)
    ```
    """
    # remove any empty lines and reverse output order
    output = [s for s in output.splitlines() if s][::-1]

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
