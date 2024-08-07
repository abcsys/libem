from libem.match import parameter
from typing import TypedDict
from collections.abc import (
    Iterable, Generator, Iterator
)

# input types
EntityDesc = str | dict


class Pair(TypedDict):
    left: EntityDesc | list[EntityDesc]
    right: EntityDesc | list[EntityDesc]


Left = EntityDesc | list[EntityDesc] | Pair | list[Pair]
Right = EntityDesc | list[EntityDesc] | None


# output types
class Answer(TypedDict):
    answer: str | float
    confidence: float | None
    explanation: str | None


Output = Answer | list[Answer]

# internal types
_EntityDesc = str
_Left = _EntityDesc | list[_EntityDesc]
_Right = _EntityDesc | list[_EntityDesc]


def parse_input(left: Left, right: Right) -> (_Left, _Right):
    if right is None:
        # when pairs are given in a single parameter,
        # parse the pair into left and right
        pair = left
        match pair:
            case dict():
                left, right = pair["left"], pair["right"]
            case _ if isinstance(pair, Iterable):
                if isinstance(pair, Generator) or isinstance(pair, Iterator):
                    pair = list(pair)
                try:
                    left = [p["left"] for p in pair]
                    right = [p["right"] for p in pair]
                except KeyError:
                    raise ValueError(
                        f"unexpected input type: {type(pair)},"
                        f"must be {Pair}."
                    )
            case _:
                raise ValueError(
                    f"unexpected input type: {type(pair)},"
                    f"must be {Pair}."
                )

    assert type(left) == type(right)

    match left:
        case str():
            pass
        case dict():
            encode = parameter.dict_desc_encoding
            left, right = encode(left), encode(right)
        case list():
            assert len(left) == len(right)
            encode = parameter.dict_desc_encoding(recurse=False)
            left = [
                encode(e) if isinstance(e, dict)
                else str(e) for e in left
            ]
            right = [
                encode(e) if isinstance(e, dict)
                else str(e) for e in right
            ]
        case _:
            raise ValueError(
                f"unexpected input type: {type(left)},"
                f"must be {Left}."
            )
    return left, right
