from libem.match import parameter
from typing import Union, Optional, TypedDict

# input types
EntityDesc = Union[str, dict]


class Pair(TypedDict):
    left: Union[EntityDesc, list[EntityDesc]]
    right: Union[EntityDesc, list[EntityDesc]]


Left = Union[
    EntityDesc, list[EntityDesc],
    Pair, list[Pair],
]
Right = Optional[
    Union[EntityDesc, list[EntityDesc]]
]


# output types
class Answer(TypedDict):
    answer: Union[str, float]
    confidence: Optional[float]
    explanation: Optional[str]


Output = Union[Answer, list[Answer]]

# internal types
_EntityDesc = str
_Left = Union[_EntityDesc, list[_EntityDesc]]
_Right = Union[_EntityDesc, list[_EntityDesc]]


def parse_input(left: Left, right: Right) -> (_Left, _Right):
    if right is None:
        # when pairs are given in a single parameter,
        # parse the pair into left and right
        pair = left
        match pair:
            case dict():
                left, right = pair["left"], pair["right"]
            case list():
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
            encode = parameter.dict_desc_encoding()
            left, right = encode(left), encode(right)
        case list():
            assert len(left) == len(right)
            encode = parameter.dict_desc_encoding()
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
