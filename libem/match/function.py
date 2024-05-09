import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
import libem.core.model as model

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
    model_output = model.call(
        prompt=Prompt.join(
            prompt.query(
                left=left,
                right=right
            ),
            prompt.rule(),
            prompt.experience(),
            prompt.output(),
        ),
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
    )
    pred = parse_output(model_output)
    libem.trace.add({"match": {"left": left, "right": right, "pred": model_output}})
    return pred


def parse_output(output: str) -> str:
    output = output.split("\n")[-1].lower()
    return "yes" if "yes" in output else "no"
