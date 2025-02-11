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

class BatchOutput(BaseModel):
    answers: list[Output]


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
    
    # count number of repeats in left and right
    left_batches, right_batches = {}, {}
    
    for l, r in zip(left, right):
        left_batches[l] = left_batches.get(l, []) + [r]
        right_batches[r] = right_batches.get(r, []) + [l]
    
    batches = left_batches if len(left_batches) <= len(right_batches) else right_batches

    # generate tasks for each batch, 
    # if smart batching is enabled, treat each cluster (size > 1) that 
    # share the same left as its own batch
    batch_tasks, curr_batch_l, curr_batch_r = [], [], []
    for left, rights in batches.items():
        if not parameter.smart_batch() or len(rights) == 1:
            # traditional batching: add pairs one by one until the batch size is reached
            for right in rights:
                curr_batch_l.append(left)
                curr_batch_r.append(right)
                
                if len(curr_batch_l) == parameter.batch_size():
                    batch_tasks.append(batch(curr_batch_l, curr_batch_r))
                    curr_batch_l, curr_batch_r = [], []
        
        else: # smart batching
            batch_start = 0
            # ensure batches do not go over the batch size
            while batch_start < len(rights):
                batch_end = batch_start + parameter.batch_size()
                batch_tasks.append(batch(left, rights[batch_start:batch_end]))
                batch_start += parameter.batch_size()
    
    # add any remaining pairs from the last traditional batch
    if len(curr_batch_l) > 0:
        batch_tasks.append(batch(curr_batch_l, curr_batch_r))
    
    return batch_tasks


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


async def batch(left: str | list[str], right: list[str]) -> list[dict]:
    start = time.time()

    output, size = [], len(right)

    # generate prompt
    system_prompt = Prompt.join(
        prompt.role(),
        prompt.rules(),
        prompt.experiences(),
        prompt.output(),
    )

    shots: list[dict] = prompt.shots()

    if isinstance(left, str):
        left_prompt = Prompt.join("Left entity:", left)
        right_prompt = Prompt.join(
            "Right entities:", 
            *[f"{i + 1}:\n{r}"
                for i, r in zip(
                    range(size), right
            )])

        match_prompt = Prompt.join(left_prompt, right_prompt)
    else:
        match_prompt = Prompt.join(*[
            Prompt.join(
                f"{i + 1}:",
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
    
    # generate output schema
    output_schema = None
    if parameter.structured():
        output_structure = {}
        if parameter.cot():
            output_structure['explanation'] = str
        output_structure['answer'] = float if parameter.likelihood() else str
        if parameter.confidence():
            output_structure['confidence'] = float
        
        # a list of the regular output schema
        output_schema = model.output_schema("Output", **{"answers": [output_structure]})

    # call the model
    response = await model.async_call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        output_schema=output_schema,
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )
    
    if parameter.structured():
        output = BatchOutput.model_validate_json(response['output']).model_dump()['answers']
        if len(output) != size: # pad output if necessary
            libem.warn(f"[match] output size differ from batch size: "
                    f"output: {len(output)}, batch size: {size}")
            
            while len(output) < size:
                output.append(Output(answer='no').model_dump())
    else:
        output_lines = response["output"].split('\n')

        # parsing model output for each pair
        # assuming model output is in the format:
        # 1: <answer>
        # 2: <answer>
        # ...
        # n: <answer>
        # where each <answer> may contain multiple lines.
        if re.match(r"^\d+:", output_lines[0]):
            answer_lines = []

            for line in output_lines:
                if re.match(r"^\d+:", line):
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

            if len(output) != size: # pad output if necessary
                libem.warn(f"[match] output size differ from batch size: "
                        f"output: {len(output)}, batch size: {size}")
                
                while len(output) < size:
                    output.append(Output(answer='no').model_dump())
        else:
            # if the model output does not follow the expected
            # format, assume all answers are the same and only
            # one answer is returned for all pairs
            libem.warn(f"[match] output size differ from batch size: "
                        f"output: 1, batch size: {size}")
            
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
