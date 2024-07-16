import random

from libem import parameter
from libem.match import func


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

    return func(left, right)


from libem.match.function import digest

_ = digest
