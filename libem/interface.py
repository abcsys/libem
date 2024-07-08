import random
import logging
from typing import Iterator
import decimal
import pprint as pp

import libem
import libem.core.model as model
from libem.core.struct import Prompt
from libem import prompt, parameter

from libem.block import func as block_func
from libem.match import func as match_func
from libem.extract import func as extract_func
from libem.tune.calibrate import func as calibrate_func
from libem.tune.calibrate import export
from libem.tune import func as tune_func

"""Chat access"""


def chat(message, context=None) -> dict:
    context = context or []
    response = model.call(
        prompt=Prompt.join(prompt.role(), message, sep="\n"),
        context=context,
        tools=["libem.match"],
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )
    return {
        "content": response["output"],
        "context": response["messages"],
    }


"""Programmatic access"""


def block(left: list, right: list) -> Iterator[dict]:
    yield from block_func(left, right)


def match(left: str | list, right: str | list) -> dict | list[dict]:
    assert type(left) == type(right)

    if isinstance(left, list):
        assert len(left) == len(right)

    if parameter.always():
        if isinstance(left, list):
            return [{
                "answer": parameter.always(),
                "confidence": None,
                "explanation": "I'm guessing.",
            } for _ in range(len(left))]
        else:
            return {
                "answer": parameter.always(),
                "confidence": None,
                "explanation": "I'm guessing.",
            }

    if parameter.guess():
        if isinstance(left, list):
            return [{
                "answer": random.choice(["yes", "no"]),
                "confidence": None,
                "explanation": "I'm guessing.",
            } for _ in range(len(left))]
        else:
            return {
                "answer": random.choice(["yes", "no"]),
                "confidence": None,
                "explanation": "I'm guessing.",
            }

    return match_func(left, right)


def extract(desc: str) -> dict:
    return extract_func(desc)


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


""" Utilities """


def pprint(*args, **kwargs):
    pp.pprint(*args, **kwargs,
              sort_dicts=False)


def round(number, n):
    return float(f"{number:.{n}g}")
