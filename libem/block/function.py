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


def func(left, right=None, key=None):
    if right is None:
        return block(left, key)
    else:
        return block_left_right(left, right, key)


def block(records: Iterable[str | dict], 
          key: str | list | None = None) -> Iterable[dict]:
    if key:
        if isinstance(key, str):
            key = [key]
        elif not isinstance(key, list):
            raise ValueError("Key must be a string or a list of strings.")
        
        # group by
        records = sorted(records, key=itemgetter(*key))
        records = itertools.groupby(records, key=itemgetter(*key))
        
        for _, group in tqdm(records, desc='Blocking'):
            # duplicate the iterable to allow for nested iteration
            left, right = itertools.tee(group, 2)
            yield from compare(left, right, 
                               remove_keys=key,
                               compare_same_index=False)
    else:
        # duplicate the iterable to allow for nested iteration
        left, right = itertools.tee(records, 2)
        yield from compare(left, right, 
                           compare_same_index=False, 
                           progress_bar=True)


def block_left_right(left: Iterable[str | dict], 
                     right: Iterable[str | dict],
                     key: str | list | None = None) -> Iterable[dict]:
    if key:
        if isinstance(key, str):
            key = [key]
        elif not isinstance(key, list):
            raise ValueError("Key must be a string or a list of strings.")
        
        # group by key
        left = sorted(left, key=itemgetter(*key))
        left = itertools.groupby(left, key=itemgetter(*key))
        right = sorted(right, key=itemgetter(*key))
        right = itertools.groupby(right, key=itemgetter(*key))
        
        # inner join the two iterables
        records = heapq.merge(right, left, key=lambda x: x[0])
        last_k, last_v = None, []
        for k, v in tqdm(records, desc='Blocking'):
            if k == last_k:
                last_k = None
                yield from compare(v, last_v, remove_keys=key)
            else:
                last_k = k
                last_v = list(v)
    else:
        yield from compare(left, right, progress_bar=True)


def compare(left: Iterable[str | dict], 
            right: Iterable[str | dict],
            remove_keys: list | None = None,
            compare_same_index: bool = True,
            progress_bar: bool = False) -> Iterable[dict]:
    ''' Block using string similarity. '''
    
    # set similarity and convert right iterable to list
    similarity = parameter.similarity()
    right = list(right)
    
    if progress_bar:
        left = tqdm(left, desc='Blocking')

    for i, l in enumerate(left):
        left_str = convert_to_str(l, remove_keys)

        for j, r in enumerate(
                tqdm(right, desc='Comparing', mininterval=0.01, leave=False)):
            if not compare_same_index and i >= j:
                continue
            
            right_str = convert_to_str(r, remove_keys)
            if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                yield {'left': l, 'right': r}


def convert_to_str(record: str | dict, remove_keys: Iterable | None = None):
    match record:
        case str():
            return record
        case dict():
            if remove_keys:
                record = record.copy()
                for key in remove_keys:
                    del record[key]
            
            return ' '.join(map(str, record.values()))
        case _:
            return str(record)
