import random

import libem
import libem.core.model as model
from libem.core.struct import Prompt
from libem import prompt, parameter

"""Chat access"""


def chat(message):
    return model.call(
        prompt=Prompt.join(prompt.role(), message, sep="\n"),
        tools=["libem.match"],
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )


"""Programmatic access"""
from libem.match import func as match_func
from libem.calibrate import func as calibrate_func
# from libem.tune import check_func
from libem.tune.function import func as tune_func


def match(left, right,
          always=None,
          guess=False) -> str:
    if always is not None:
        return always

    if guess:
        random.seed(libem.LIBEM_SEED)
        return random.choice(["yes", "no"])

    return match_func(left, right)


def calibrate(*args, **kwargs):
    return calibrate_func(*args, **kwargs)


def tune(*args, **kwargs):
    return tune_func(*args, **kwargs)
