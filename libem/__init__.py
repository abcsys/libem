import random

from libem.constant import *

import libem.core.model as model
from libem.core.struct import Prompt
import libem.prompt as prompt
from libem import parameter
from libem import match as match_tool


def chat(message):
    """Simple chat interface for libem"""
    return model.call(prompt=Prompt.join(prompt.role(), message, sep="\n"),
                      model=parameter.model(),
                      tools=[match_tool])


from libem.match import function


def match(left, right,
          always=None,
          guess=False,
          seed=42) -> bool:
    """Programming interface for entity matching"""
    if always is not None:
        return always

    if guess:
        random.seed(seed)
        return random.choice([True, False])

    return function.match(left, right)
