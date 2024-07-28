from typing import Iterator
from fuzzywuzzy import fuzz

from libem.block import parameter

schema = {
    "type": "function",
    "function": {
        "name": "block",
        "description": "Perform the blocking stage of entity matching given two datasets.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "list",
                    "description": "A list containing the first dataset.",
                },
                "right": {
                    "type": "list",
                    "description": "A list containing the second dataset.",
                },
            },
            "required": ["left"],
        },
    }
}


def func(left, right=None):
    if right is None:
        block(left)
    else:
        return block_left_right(left, right)


def block(records: Iterator[str] | Iterator[dict]) -> Iterator[dict]:
    similarity = parameter.similarity()

    left, right = records, records

    for i, l in enumerate(left):
        left_str = convert_to_str(l)
        for j, r in enumerate(right):
            if i == j:
                continue
            right_str = convert_to_str(r)
            if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                yield {'left': l, 'right': r}


def block_left_right(left: Iterator[str | dict], right: Iterator[str | dict]) -> Iterator[dict]:
    similarity = parameter.similarity()

    for l in left:
        left_str = convert_to_str(l)
        for r in right:
            right_str = convert_to_str(r)
            if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                yield {'left': l, 'right': r}


def convert_to_str(record):
    if isinstance(record, dict):
        return ' '.join(map(str, record.values()))
    return str(record)
