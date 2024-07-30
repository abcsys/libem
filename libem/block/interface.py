from typing import TypedDict
from collections.abc import Iterator

from libem.block.function import func

EntityDesc = str | dict

Left = Iterator[EntityDesc]
Right = Iterator[EntityDesc] | None


class Pair(TypedDict):
    left: EntityDesc | list[EntityDesc]
    right: EntityDesc | list[EntityDesc]


Output = Iterator[Pair]


def block(left: Left, right: Right = None) -> Output:
    yield from func(left, right)
