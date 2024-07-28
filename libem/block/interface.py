from typing import Iterator

from libem.block import func


def block(
        left: Iterator[str | dict],
        right: Iterator[str | dict] | None
) -> Iterator[dict]:
    yield from func(left, right)
