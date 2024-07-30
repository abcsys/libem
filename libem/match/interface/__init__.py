import random

from libem.match import (
    parameter,
    func, async_func,
)
from libem.match.interface.struct import (
    Left, Right, Output,
    parse_input,
)


def match(left: Left, right: Right = None) -> Output:
    left, right = parse_input(left, right)

    # random guessing
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


async def async_match(left: Left, right: Right) -> Output:
    return await async_func(left, right)


from libem.match.function import digest

_ = digest
