from tqdm import tqdm
from fuzzywuzzy import fuzz
from collections.abc import Iterator

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
        return block(left)
    else:
        return block_left_right(left, right)


def block(records: Iterator[str | dict]) -> Iterator[dict]:
    similarity = parameter.similarity()

    for i, l in enumerate(
            tqdm(records, desc='Blocking')):
        left_str = convert_to_str(l)
        for j, r in enumerate(
                tqdm(records, desc='Comparing', leave=False)):
            if i != j:
                right_str = convert_to_str(r)
                if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                    yield {'left': l, 'right': r}


def block_left_right(left: Iterator[str | dict], right: Iterator[str | dict]) -> Iterator[dict]:
    similarity = parameter.similarity()

    for l in tqdm(left, desc='Blocking'):
        left_str = convert_to_str(l)
        for r in tqdm(right, desc='Comparing', leave=False):
            right_str = convert_to_str(r)
            if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                yield {'left': l, 'right': r}


def convert_to_str(record: str | dict):
    match record:
        case str():
            return record
        case dict():
            return ' '.join(map(str, record.values()))
        case _:
            return str(record)
