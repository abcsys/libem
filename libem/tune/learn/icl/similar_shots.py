"""
Use similarity metric to find similar examples in the training data.
"""

from fuzzywuzzy import fuzz

from libem.core.struct.prompt import Shots


def run(shots: Shots,
        question: str,
        num_shots: int) -> Shots:
    similar_shots = []
    for shot in shots:
        ratio = fuzz.token_set_ratio(
            shot.question, question
        )
        similar_shots.append(
            (shot, ratio)
        )
    similar_shots.sort(key=lambda x: x[1], reverse=True)

    return Shots([
        shot for shot, _ in similar_shots[:num_shots]
    ])
