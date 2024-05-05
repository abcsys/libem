import random

from libem.constant import *

import libem.core.model as model
from libem.core.struct import Prompt

from libem import prompt, parameter
from libem import match as match_tool


def chat(message):
    """Simple chat interface for libem"""
    return model.call(
        prompt=Prompt.join(prompt.role(), message, sep="\n"),
        tools=[match_tool],
        model=parameter.model(),
        temperature=parameter.temperature(),
    )


from libem.match import function


def match(left, right,
          always=None,
          guess=False,
          seed=42) -> str:
    """Programming interface for entity matching"""
    if always is not None:
        return always

    if guess:
        random.seed(seed)
        return random.choice(["yes", "no"])

    return function.match(left, right)
