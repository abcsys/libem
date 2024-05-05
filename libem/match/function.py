import libem.core.model as model
from libem import browse
from libem import parameter
from libem.match import prompt
from libem.core.struct import Prompt

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
    return match(left, right)


def match(left, right):
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
        model=parameter.model(),
        tools=[browse]
    )
