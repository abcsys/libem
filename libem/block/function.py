import heapq
import itertools
from tqdm import tqdm
from fuzzywuzzy import fuzz
from operator import itemgetter
from collections.abc import Iterable

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


def func(left: Iterable[str | dict], 
         right: Iterable[str | dict] | None = None, 
         on: str | list | None = None) -> Iterable[dict]:
    if right is None:
        return block(left, on)
    else:
        return block_left_right(left, right, on)


def block(records: Iterable[str | dict], 
          on: str | list | None = None) -> Iterable[dict]:
    if on:
        # group by
        if isinstance(on, str):
            records = sorted(records, key=itemgetter(on))
            records = itertools.groupby(records, key=itemgetter(on))
        elif isinstance(on, list):
            records = sorted(records, key=itemgetter(*on))
            records = itertools.groupby(records, key=itemgetter(*on))
        
        for _, group in tqdm(records, desc='Blocking'):
            # duplicate the iterable to allow for nested iteration
            left, right = itertools.tee(group, 2)
            yield from block_similarity(left, right, block_same_index=False)
    else:
        # duplicate the iterable to allow for nested iteration
        left, right = itertools.tee(records, 2)
        yield from block_similarity(left, right, 
                                    block_same_index=False, 
                                    progress_bar=True)


def block_left_right(left: Iterable[str | dict], 
                     right: Iterable[str | dict],
                     on: str | list | None = None) -> Iterable[dict]:
    if on:
        # group by
        if isinstance(on, str):
            left = sorted(left, key=itemgetter(on))
            left = itertools.groupby(left, key=itemgetter(on))
            right = sorted(right, key=itemgetter(on))
            right = itertools.groupby(right, key=itemgetter(on))
        elif isinstance(on, list):
            left = sorted(left, key=itemgetter(*on))
            left = itertools.groupby(left, key=itemgetter(*on))
            right = sorted(right, key=itemgetter(*on))
            right = itertools.groupby(right, key=itemgetter(*on))
        
        # inner join the two iterables
        records = heapq.merge(left, right, key=lambda x: x[0])
        last_key, last_val = None, []
        for key, val in tqdm(records, desc='Blocking'):
            if key == last_key:
                last_key = None
                yield from block_similarity(last_val, val)
            else:
                last_key = key
                last_val = list(val)
    else:
        yield from block_similarity(left, right, progress_bar=True)


def block_similarity(left: Iterable[str | dict], 
                     right: Iterable[str | dict],
                     block_same_index: bool = True,
                     progress_bar: bool = False) -> Iterable[dict]:
    ''' Block using string similarity. '''
    
    # set similarity and convert right iterable to list
    similarity = parameter.similarity()
    right = list(right)
    
    if progress_bar:
        left = tqdm(left, desc='Blocking')

    for i, l in enumerate(left):
        left_str = convert_to_str(l)

        for j, r in enumerate(
                tqdm(right, desc='Comparing', mininterval=0.01, leave=False)):
            if not block_same_index and i >= j:
                continue
            
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
