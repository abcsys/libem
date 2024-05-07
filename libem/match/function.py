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
    return model.call(
        prompt=Prompt.join(
            prompt.query(
                left=left,
                right=right
            ),
            prompt.output(),
            prompt.rule(),
            prompt.experience()
        ),
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
    )
