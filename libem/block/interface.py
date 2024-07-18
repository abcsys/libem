from typing import Iterator

from libem.block import func


def block(left: list, right: list) -> Iterator[dict]:
    yield from func(left, right)
