from libem.core.struct import prompt


def run(shots: prompt.Shots,
        question: str = None,
        num_shots: int = -1) -> prompt.Shots:
    if num_shots > 0:
        shots = shots[:min(num_shots, len(shots))]
    _ = question
    return shots
