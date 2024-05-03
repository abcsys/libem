import random

from libem.constant import *
from libem.match import function


def match(left, right,
          always=None,
          guess=False,
          seed=42) -> bool:
    if always is not None:
        return always

    if guess:
        random.seed(seed)
        return random.choice([True, False])

    return function.match(left, right)
