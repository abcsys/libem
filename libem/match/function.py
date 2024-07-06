import re
import time
from pprint import pformat
from typing import Any
import hashlib

import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
from libem.core import struct
from libem.core import model

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
         right: Any | list[Any]) -> Any | list[Any]:
    if parameter.batch():
        assert len(left) == len(right)
        left_batches, right_batches, batch_ids = [], [], []
        
        # generate batches
        i = 0
        while i < len(left):
            left_batches.append([left[i+j]
                for j in range(min(parameter.batch_size(), len(left) - i))]
            )
            right_batches.append([right[i+j]
                for j in range(min(parameter.batch_size(), len(left) - i))]
            )
            batch_ids.append([digest(left[i+j], right[i+j]) 
                for j in range(min(parameter.batch_size(), len(left) - i))])
            i += parameter.batch_size()
        
        output = []
        for l, r, ids in zip(left_batches, right_batches, batch_ids):
            output.extend(batch_match(l, r, ids))
        
        return output
    else:
        return match(left, right)
    

def match(left, right) -> dict:
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

    response = model.call(
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

def batch_match(left: list[Any], right: list[Any], ids: list[Any]) -> list[dict]:
    start = time.time()
    output = []
    
    system_prompt = Prompt.join(
        prompt.role(),
        prompt.rules(),
        prompt.experiences(),
        prompt.output(),
    )

    shots: list[dict] = prompt.shots()
    
    match_prompt = Prompt.join(*[
        Prompt.join(
            f"Q{i+1}:",
            prompt.query(
                left=l,
                right=r
            )
        )
        for i, l, r in zip(range(len(left)), left, right)]
    )

    _prompt = [
        {"role": "system", "content": system_prompt},
        *shots,
        {"role": "user", "content": match_prompt},
    ]

    response = model.call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )
    
    model_answer = response["output"].split('\n')
    # if model only gives a single answer, assume all pairs are that answer
    if not re.match(r"^Q\d+:", model_answer[0]):
        answer = parse_output(response["output"])
        output.extend([answer for _ in ids])
    else:
        # split model output into individual pairs
        current_lines = []
        for line in model_answer:
            if re.match(r"^Q\d+:", line):
                if len(current_lines) > 0:
                    out = parse_output('\n'.join(current_lines))
                    output.append(out)
                current_lines = []
            current_lines.append(line)
        if len(current_lines) > 0:
            out = parse_output('\n'.join(current_lines))
            output.append(out)
    
    libem.trace.add({
        "batch_match": {
            "ids": ids,
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
