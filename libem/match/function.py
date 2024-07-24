import re
import time
import hashlib
from tqdm import tqdm
from itertools import chain
from pprint import pformat
from typing import Coroutine

import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
from libem.core import (
    exec, model, struct
)

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


def func(left: str | list[str], right: str | list[str]) -> dict | list[dict]:
    if parameter.sync():
        return sync_func(left, right)
    else:
        return exec.run_async_task(
            async_func(left, right)
        )


def sync_func(left: str | list[str], right: str | list[str]) -> dict | list[dict]:
    if isinstance(left, str):
        return exec.run_async_task(
            once(left, right)
        )

    if parameter.batch_size() == 1:
        tasks = create_once_tasks(left, right)
    else:
        tasks = create_batch_tasks(left, right)

    output = []
    for task in tqdm(tasks):
        output.extend(
            exec.run_async_task(task)
        )

    return output


async def async_func(left: str | list[str], right: str | list[str]) -> dict | list[dict]:
    if isinstance(left, str):
        return await once(left, right)

    if parameter.batch_size() == 1:
        tasks = create_once_tasks(left, right)
    else:
        tasks = create_batch_tasks(left, right)

    return list(chain.from_iterable(
        await exec.proc_async_tasks(tasks)
    ))


def create_once_tasks(left: list[str], right: list[str]) -> list[Coroutine]:
    async def _once(left, right):
        # wrap the result in a list to
        # follow the batch output format

        return [await once(left, right)]

    return [
        _once(left, right)
        for left, right in zip(left, right)
    ]


def create_batch_tasks(left: list[str], right: list[str]) -> list[Coroutine]:
    assert len(left) == len(right)

    num_pairs = len(left)
    batch_size = parameter.batch_size()
    left_batches, right_batches = [], []
    batch_start = 0

    # generate left and right batches
    while batch_start < num_pairs:
        batch_end = min(batch_start + batch_size, num_pairs)

        left_batches.append(
            left[batch_start:batch_end]
        )
        right_batches.append(
            right[batch_start:batch_end]
        )

        batch_start += batch_size

    # generate tasks for each batch
    return [
        batch(left, right)
        for left, right in zip(left_batches, right_batches)
    ]


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

    shots = parameter.icl_strategy().run(
        shots=prompt.shots,
        question=prompt.query(left=left, right=right),
        num_shots=parameter.num_shots(),
    )

    _prompt = [
        {"role": "system", "content": system_prompt},
        *shots(),
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


async def batch(left: list[str], right: list[str]) -> list[dict]:
    start = time.time()

    output, size = [], len(left)

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

        if len(output) > size:
            libem.warn(f"[match] output size greater than batch size: "
                       f"output: {output}; {len(output)} > {size}")
    else:
        # if the model output does not follow the expected
        # format, assume all answers are the same and only
        # one answer is returned for all pairs
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


def digest(left: str, right: str) -> str:
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
    # remove empty lines and process lines in reverse order
    output = [s for s in output.splitlines() if s][::-1]

    answer = output.pop(0).lower()
    answer = "yes" if "yes" in answer else "no"

    confidence, explanation = None, None

    if parameter.confidence():
        for i, line in enumerate(output):
            line = line.lower()
            nums = re.findall(r"\d+\.\d+|\d+", line)
            if nums:
                confidence = float(''.join(nums))
                output = output[i + 1:]
                break

    if parameter.cot():
        explanation = "\n".join(output[::-1])

    return {
        "answer": answer,
        "confidence": confidence,
        "explanation": explanation,
    }
