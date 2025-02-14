import heapq
import itertools
from tqdm import tqdm
from fuzzywuzzy import fuzz
from operator import itemgetter
from typing import Any, Callable, Iterable
from multiprocessing import Pool, cpu_count

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


def func(left, right=None, key=None, ignore=None):
    if right is None:
        return block(left, key, ignore)
    else:
        return block_left_right(left, right, key, ignore)


def block(records: Iterable[str | dict], 
          key: str | list | None = None,
          ignore: str | list | None = None) -> Iterable[dict]:
    
    if not ignore:
        ignore = []
    elif isinstance(ignore, str):
        ignore = [ignore]
    elif not isinstance(ignore, list):
        raise ValueError("Ignore must be a string or a list of strings.")
    
    if key:
        if isinstance(key, str):
            key = [key]
        elif not isinstance(key, list):
            raise ValueError("Key must be a string or a list of strings.")
        
        # group by key
        grouped_records = list(parallel_groupby(records, key=itemgetter(*key)).values())
        
        return parallel_block_left_right(grouped_records, grouped_records,
                                         remove_keys=key + ignore, 
                                         compare_same_index=False)
    else:
        records = list(records)
        return parallel_block_left_right(records, records, 
                                         remove_keys=ignore, 
                                         compare_same_index=False)


def block_left_right(left: Iterable[str | dict], 
                     right: Iterable[str | dict],
                     key: str | list | None = None,
                     ignore: str | list | None = None) -> Iterable[dict]:
    if not ignore:
        ignore = []
    elif isinstance(ignore, str):
        ignore = [ignore]
    elif not isinstance(ignore, list):
        raise ValueError("Ignore must be a string or a list of strings.")
    
    if key:
        if isinstance(key, str):
            key = [key]
        elif not isinstance(key, list):
            raise ValueError("Key must be a string or a list of strings.")
        
        # group by key
        left = parallel_groupby(left, key=itemgetter(*key))
        right = parallel_groupby(right, key=itemgetter(*key))
        
        # inner join the two iterables
        common_keys = set(left.keys()) & set(right.keys())
        left_list = [left[key] for key in common_keys]
        right_list = [right[key] for key in common_keys]
        return parallel_block_left_right(
            left_list, right_list,
            remove_keys=key + ignore
        )
    else:
        left, right = list(left), list(right)
        return parallel_block_left_right(left, right, 
                                         remove_keys=ignore)


def parallel_groupby(data: Iterable[Any], key: Callable[[Any], Any]) -> dict:
    ''' Perform a parallelized groupby operation on an iterable. '''
    
    # Convert data to a list for slicing
    data = list(data)
    chunk_size = max(1, len(data) // cpu_count())
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Process chunks in parallel
    with Pool(cpu_count()) as pool:
        args = [(chunk, key) for chunk in chunks]
        chunk_results = pool.starmap(groupby_chunk, args)

    # Merge results
    grouped_result = {}
    for partial_result in chunk_results:
        for k, v in partial_result.items():
            if k in grouped_result:
                grouped_result[k].extend(v)
            else:
                grouped_result[k] = v

    return grouped_result


def groupby_chunk(chunk: list[Any], key: Callable[[Any], Any]) -> dict:
    """Group a single chunk."""
    chunk = sorted(chunk, key=key)  # Groupby requires sorted input
    return {k: list(g) for k, g in itertools.groupby(chunk, key=key)}


def parallel_block_left_right(left: list[str | dict | list],
                              right: list[str | dict | list],
                              remove_keys: list | None = None,
                              compare_same_index: bool = True) -> list[dict]:
    ''' Run block with multiprocessing. '''
    
    with Pool(cpu_count()) as pool:
        if isinstance(left[0], list): # nested list: pass each sublist to compare
            if not isinstance(right[0], list):
                raise ValueError("Left and right must have the same structure.")
            
            async_results = [
                pool.apply_async(
                    compare, 
                    args=(l, r, remove_keys, compare_same_index)
                )
                for l, r in zip(left, right)
            ]
        else: # single list: split into chunks
            if isinstance(right[0], list):
                raise ValueError("Left and right must have the same structure.")
            
            left_size = len(left)
            chunk_size = max(1, left_size // cpu_count())
            left_chunks = [left[i:i + chunk_size] for i in range(0, left_size, chunk_size)]
            async_results = []
            
            if compare_same_index:
                async_results = [
                    pool.apply_async(
                        compare, 
                        args=(left_chunks[l], right, remove_keys)
                    )
                    for l in range(len(left_chunks))
            ]
            else:
                right_size = len(right)
                if left_size != right_size:
                    raise ValueError("Left and right must have the same length.")
                
                async_results = [
                    pool.apply_async(
                        compare, 
                        args=(left_chunks[l], right[l*chunk_size:], remove_keys, compare_same_index)
                    )
                    for l in range(len(left_chunks))
                ]
        
        # Monitor progress and collect results
        results = []
        with tqdm(total=len(async_results), desc="Blocking") as pbar:
            for async_result in async_results:
                try:
                    results.extend(async_result.get())
                    pbar.update(1)
                except Exception as e:
                    # terminate the pool if an exception occurs
                    pool.terminate()
                    pool.join()
                    raise e
    
    return results


def compare(left: Iterable[str | dict], 
            right: Iterable[str | dict],
            remove_keys: list | None = None,
            compare_same_index: bool = True,
            progress_bar: bool = False) -> Iterable[dict]:
    ''' Block using string similarity. '''
    
    # set similarity and convert right iterable to list
    similarity = parameter.similarity()
    right = list(right)
    result = []

    for i, l in enumerate(left):
        left_str = convert_to_str(l, remove_keys)
        
        iterable = right
        if progress_bar:
            iterable = tqdm(right, desc='Comparing', mininterval=0.01, leave=False)

        for j, r in enumerate(iterable):
            if not compare_same_index and i >= j:
                continue
            
            right_str = convert_to_str(r, remove_keys)
            if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                result.append({'left': l, 'right': r})
    
    return result


def convert_to_str(record: str | dict, remove_keys: Iterable | None = None):
    match record:
        case str():
            return record
        case dict():
            if remove_keys:
                return ' '.join(map(str, (value for key, value in record.items() if key not in remove_keys)))
            else:
                return ' '.join(map(str, record.values()))
        case _:
            return str(record)
