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

from libem.match.interface import match
from libem.block.interface import block
from libem.extract.interface import extract
from libem.resolve.cluster.interface import cluster
from libem.resolve.dedupe.interface import dedupe
from libem.resolve.link.interface import link

_ = match, block, extract, cluster, dedupe, link

from libem.tune.calibrate.interface import (
    calibrate, export
)

_ = calibrate, export

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
from libem.prepare.datasets.clustering import datasets


def load(name, num_samples=-1):
    if name not in datasets:
        raise ValueError(f"Dataset '{name}' not found.")
    _load = datasets[name]
    return _load(num_samples=num_samples)


def pprint(*args, **kwargs):
    pp.pprint(
        *args, **kwargs,
        sort_dicts=False
    )


def pformat(*args, **kwargs):
    return pp.pformat(
        *args, **kwargs,
        sort_dicts=False
    )


def display_mode():
    import pandas as pd
    pd.set_option('display.max_rows', None)


def round(number, n=3):
    return float(f"{number:.{n}g}")
