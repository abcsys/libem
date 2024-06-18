from libem.core import model
from libem.core.struct import Prompt
from libem.extract import parameter, prompt

schema = {}


def func(desc: str):
    response = model.call(
        prompt=Prompt.join(
            prompt.role(),
            prompt.query(desc=desc),
            prompt.output(),
        ),
        model=parameter.model(),
        temperature=parameter.temperature(),
    )
    return response["output"]
