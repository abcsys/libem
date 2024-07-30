from typing import (
    Iterator, Union, Optional,
    TypedDict,
)

from libem.block.function import func

EntityDesc = Union[str, dict]

Left = Iterator[EntityDesc]
Right = Optional[Iterator[EntityDesc]]


class Pair(TypedDict):
    left: Union[EntityDesc, list[EntityDesc]]
    right: Union[EntityDesc, list[EntityDesc]]


Output = Iterator[Pair]


def block(left: Left, right: Right = None) -> Output:
    yield from func(left, right)
