"""Randomly select examples from training data as the prompt."""

import random

from libem.core.struct.prompt import Shots


def run(shots: Shots,
        question: str = None,
        num_shots: int = 1) -> Shots:
    return Shots(
        random.sample(list(shots), num_shots)
    )
