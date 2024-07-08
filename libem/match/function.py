import re
import time
from pprint import pformat
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


def func(left: str | list, right: str | list) -> dict | list[dict]:
    assert type(left) == type(right)

    if parameter.batch_size() > 1:
        return batch(left, right)
    else:
        return once(left, right)


def once(left: str, right: str) -> dict:
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


def batch(left: list, right: list) -> list[dict]:
    assert len(left) == len(right)

    num_pairs = len(left)
    batch_size = parameter.batch_size()
    left_batches, right_batches, pair_ids = [], [], []
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

    num_batches = len(left_batches)

    output = []
    for i, (l, r) in enumerate(zip(left_batches, right_batches)):
        if not parameter.quiet():
            libem.info(f"[match] processing batch "
                       f"{i + 1} / {num_batches} "
                       f"of size {len(l)}.")
        output.extend(_proc_batch(l, r))

    return output


def _proc_batch(left: list, right: list) -> list[dict]:
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

    response = model.call(
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
