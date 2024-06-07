import random

import libem
import libem.core.model as model
from libem.core.struct import Prompt
from libem import prompt, parameter

from libem.match import func as match_func
from libem.tune.calibrate import func as calibrate_func
from libem.tune.calibrate import export
from libem.tune import func as tune_func

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


def match(left, right) -> str:
    if parameter.always():
        return parameter.always()

    if parameter.guess():
        random.seed(libem.LIBEM_SEED)
        return random.choice(["yes", "no"])

    return match_func(left, right)


def calibrate(*args, **kwargs):
    return calibrate_func(*args, **kwargs)


def tune(*args, **kwargs):
    return tune_func(*args, **kwargs)


def config():
    return export(
        toolchain="libem",
        nest=True,
    )
