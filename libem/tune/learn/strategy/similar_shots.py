"""
Use similarity metric to find similar examples in the training data.
"""

from fuzzywuzzy import fuzz

from libem.core.struct import Shot
from libem.match.prompt import (
    query, Prompt
)


def run(dataset, pair, num_shots: int = 3) -> Prompt.Shots:
    shots = []

    for shot in dataset:
        ratio = fuzz.token_set_ratio(pair, shot)
        shots.append((
            Shot(
                question=query(
                    left=shot["left"],
                    right=shot["right"],
                ),
                answer="yes" if shot["label"] else "no",
            ), ratio)
        )
    shots.sort(key=lambda x: x[1], reverse=True)

    return Prompt.Shots([
        shot[0] for shot in shots[:num_shots]
    ])
