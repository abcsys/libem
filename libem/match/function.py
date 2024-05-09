import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
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


def func(left, right):
    match_prompt = Prompt.join(
        prompt.query(
            left=left,
            right=right
        ),
        prompt.rule(),
        prompt.experience(),
        prompt.output(),
    )
    pred = parse_output(model.call(
        prompt=match_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
    ))
    libem.trace.add({"match": {"left": left, "right": right, "pred": pred,
                               "prompt": match_prompt}})
    return pred


def parse_output(output: str) -> str:
    libem.debug("Match raw output:", output)
    output = output.split("\n")[-1].lower()
    return "yes" if "yes" in output else "no"
