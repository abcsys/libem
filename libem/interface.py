import random

import libem.core.model as model
from libem.core.struct import Prompt

from libem import prompt, parameter

"""Chat interface"""


def chat(message):
    return model.call(
        prompt=Prompt.join(prompt.role(), message, sep="\n"),
        tools=["libem.match"],
        model=parameter.model(),
        temperature=parameter.temperature(),
    )


"""Programming interface"""
from libem.match import func as match_func


def match(left, right,
          always=None,
          guess=False,
          seed=42) -> str:
    if always is not None:
        return always

    if guess:
        random.seed(seed)
        return random.choice(["yes", "no"])

    return match_func(left, right)


from libem.calibrate import func as calibrate_func


def calibrate(*args, **kwargs):
    return calibrate_func(*args, **kwargs)
