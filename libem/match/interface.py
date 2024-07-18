import random
from typing import Union

from libem import parameter
from libem.match import func, async_func

input_type = Union[
    str, list[str]
]

output_type = Union[
    dict, list[dict]
]


def match(left: input_type, right: input_type) -> output_type:
    # input validation
    assert type(left) == type(right)

    match left:
        case str():
            pass
        case list():
            assert len(left) == len(right)
        case _:
            raise ValueError(
                f"unexpected input type: {type(left)},"
                f"must be {input_type}."
            )

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


async def async_match(left: input_type, right: input_type) -> output_type:
    return await async_func(left, right)


from libem.match.function import digest

_ = digest
