import re
import time
import hashlib
from pydantic import BaseModel
from tqdm import tqdm
from itertools import chain
from pprint import pformat
from typing import Coroutine

import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
from libem.core import (
    exec, model
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


class Output(BaseModel):
    answer: str | float
    confidence: float = None
    explanation: str = None


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
        await exec.proc_async_tasks(tasks, rpm=parameter.rpm(), desc="Matching")
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
        prompt.CoT() if parameter.cot() else "",
        prompt.output(),
        prompt.Confidence() if parameter.confidence() else "",
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
        {"role": parameter.system_role(), "content": system_prompt},
        *shots(),
        {"role": "user", "content": match_prompt},
    ]

    output_schema = None
    if parameter.structured():
        output_structure = {}
        if parameter.cot():
            output_structure['explanation'] = str
        output_structure['answer'] = float if parameter.likelihood() else str
        if parameter.confidence():
            output_structure['confidence'] = float
            
        output_schema = model.output_schema("Output", **output_structure)

    response = await model.async_call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        output_schema=output_schema,
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )

    libem.debug(f"[match] prompt:\n"
                f"{pformat(_prompt, sort_dicts=False)}\n"
                f"[match] model output:\n"
                f"{response['output']}")

    if parameter.structured():
        output = Output.model_validate_json(response['output']).model_dump()
    else:
        output = parse_output(response['output'])
    
    if parameter.likelihood():
        output['likelihood'] = output['answer']
        output['answer'] = 'no' if output['likelihood'] < 0.5 else 'yes'

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
        {"role": parameter.system_role(), "content": system_prompt},
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
    <answer> (e.g., yes)
    <confidence> (e.g., "Confidence Score: 0.9" or "0.9")
    ```
    """
    # remove empty lines and process lines in reverse order
    output = [s for s in output.splitlines() if s][::-1]
    
    index = 0
    answer, confidence, explanation = None, None, None
    
    # parse for numeric values (confidence, likelihood)
    # with priority given to likelihood if 
    # both are enabled but only 1 value is found
    numeric_vals = []
    num_numeric_vals = parameter.confidence() + parameter.likelihood()

    while index < len(output):
        if len(numeric_vals) == num_numeric_vals:
            break
        
        nums = re.findall(r"\d+\.\d+|\d+", output[index])
        if nums:
            # append new values to front of the list so likelihood
            # always comes before confidence even if both are from the same line
            numeric_vals = [float(n) for n in nums] + numeric_vals
        
        index += 1
    
    # parse answer
    if parameter.likelihood():
        if len(numeric_vals) > 0:
            answer = float(numeric_vals.pop(0))
        else:
            answer = 0.0
    else:
        # if there are no more lines left, look at previous line
        if index == len(output):
            index -= 1
        line = output[index].lower()
        index += 1
        
        answer = "yes" if "yes" in line else "no"
    
    # parse confidence
    if parameter.confidence() and len(numeric_vals) > 0:
        confidence = float(numeric_vals[-1])
    
    # parse explanation
    if parameter.cot() and index < len(output):
        explanation = "\n".join(output[index::-1])

    return {
        "answer": answer,
        "confidence": confidence,
        "explanation": explanation,
    }
