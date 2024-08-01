from typing import TypedDict
from collections.abc import Iterable

from libem.block.function import func

EntityDesc = str | dict

Left = Iterable[EntityDesc]
Right = Iterable[EntityDesc] | None


class Pair(TypedDict):
    left: EntityDesc | list[EntityDesc]
    right: EntityDesc | list[EntityDesc]


Output = Iterable[Pair]


def block(left: Left, right: Right = None) -> Output:
    yield from func(left, right)
