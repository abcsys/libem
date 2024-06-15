import logging
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


def match(left, right) -> dict:
    if parameter.always():
        return {
            "answer": parameter.always(),
            "confidence": None,
            "explanation": "I'm guessing.",
        }

    if parameter.guess():
        return {
            "answer": random.choice(["yes", "no"]),
            "confidence": None,
            "explanation": "I'm guessing.",
        }

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


def debug_on():
    libem.LIBEM_LOG_LEVEL = logging.DEBUG


def quiet():
    libem.LIBEM_LOG_LEVEL = logging.WARNING


def seed(seed=42):
    libem.LIBEM_SEED = seed
    random.seed(seed)
