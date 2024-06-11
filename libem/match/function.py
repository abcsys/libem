import time
from pprint import pformat

import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
from libem.core import struct
from libem.core import model

schema = {
    "type": "function",
    "function": {
        "name": "match",
        "description": "Perform entity matching given two entity description.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "string",
                    "description": "Description of the first entity",
                },
                "right": {
                    "type": "string",
                    "description": "Description of the second entity",
                },
            },
            "required": ["left", "right"],
        },
    }
}


def func(left, right) -> dict:
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

    model_output = model.call(
        prompt=_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )

    libem.debug(f"[match] prompt:\n"
                f"{pformat(_prompt, sort_dicts=False)}\n"
                f"[match] model output:\n"
                f"{model_output}")

    output = parse_output(model_output)

    libem.trace.add({"match": {"left": left, "right": right,
                               "prompt": _prompt,
                               "model_output": model_output,
                               "answer": output["answer"],
                               "latency": time.time() - start}})
    return output


def parse_output(output: str) -> dict:
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
