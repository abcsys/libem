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
            "required": ["left", "right"],
        },
    }
}


def func(left: list[str | dict], right: list[str | dict]) -> Iterator[dict]:
    right_strs = []

    for l in left:
        if type(l) is dict:
            left_vals = []
            for v in l.values():
                left_vals.append(str(v))
            left_str = ' '.join(i for i in left_vals)
        else:
            left_str = l

        for i, r in enumerate(right):
            if len(right_strs) > i:
                right_str = right_strs[i]
            else:
                if type(r) is dict:
                    right_vals = []
                    for v in r.values():
                        right_vals.append(str(v))
                    right_str = ' '.join(i for i in right_vals)
                else:
                    right_str = l
                right_strs.append(right_str)

            if fuzz.token_set_ratio(left_str, right_str) >= parameter.similarity():
                yield {'left': l, 'right': r}
