import random
import logging
import pprint as pp

import libem
import libem.core.model as model
from libem.core.struct import Prompt
from libem import prompt, parameter

""" Chat access to tools """


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


""" Programmatic access to tools """

from libem.match import match
from libem.block import block
from libem.extract import extract
from libem.tune.calibrate import (
    calibrate, export
)

_ = match, block, extract, calibrate, export

""" Configurations """


def config():
    return export(
        toolchain="libem",
        nest=True,
    )


def reset():
    model.reset()


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
