import time

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


def func(left, right) -> str | tuple[str, int]:
    start = time.time()

    system_prompt = Prompt.join(
        prompt.role(),
        prompt.rule(),
        prompt.experience(),
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

    model_output = model.call(
        prompt=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": match_prompt},
        ],
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )
    libem.debug(f"[match] prompt:\n{system_prompt}\n{match_prompt}\n\n"
                f"[match] raw output:\n{model_output}")

    pred, confidence = parse_output(model_output)

    libem.trace.add({"match": {"left": left, "right": right, "model_output": model_output,
                               "pred": pred, "prompt": match_prompt,
                               "latency": time.time() - start}})

    if parameter.confidence():
        return pred, confidence
    else:
        return pred


def parse_output(output: str) -> tuple[str, int | None]:
    output = [line.lower() for line in output.split("\n")]

    answer = "yes" if "yes" in output[-1] else "no"

    confidence = None

    if parameter.confidence():
        for i, line in enumerate(list(reversed(output))):
            if 'confidence score' in line:
                confidence = ''.join(filter(str.isdigit, line))

                # catch cases when score is on a new line
                if len(confidence) == 0:
                    confidence = ''.join(filter(str.isdigit, output[i - 1]))

                confidence = int(confidence)
                break

    return answer, confidence
