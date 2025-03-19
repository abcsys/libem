import ray
from ray.data.aggregate import AggregateFnV2
from ray.data.block import BlockAccessor
from fuzzywuzzy import fuzz
from itertools import combinations, product
from typing import Any
from tqdm import tqdm

from libem.block import parameter
from libem.block.struct import (
    _TextRecord, _ImageRecord, 
    _Record, parse_input
)
from libem.struct import Record

schema = {
    "type": "function",
    "function": {
        "name": "block",
        "description": "Perform the blocking stage of entity matching given one or more datasets.",
        "parameters": {
            "type": "object",
            "properties": {
                "records": {
                    "type": "array",
                    "items": {
                        "type": "list",
                        "description": "A list containing a dataset.",
                    },
                },
            },
            "required": ["records"],
        },
    }
}


def func(*records: Record, 
         key: str | list | None = None,
         ignore: str | list | None = None) -> list[dict]:
    
    if not ignore:
        ignore = []
    elif isinstance(ignore, str):
        ignore = [ignore]
    elif not isinstance(ignore, list):
        raise ValueError("Ignore must be a string or a list of strings.")
    
    if not key:
        key = None
    elif isinstance(key, str):
        key = [key]
    elif not isinstance(key, list):
        raise ValueError("Key must be a string or a list of strings.")
        
    grouped_records = process(records, key)
    
    if len(records) == 1:
        return block_single_list(grouped_records, ignore)
    else:
        return block_across_lists(grouped_records, ignore)


def process(records: Record, key: list[str] | None) -> list[dict]:
    ''' 
    Process and perform groupby operations on the records.
    If multiple datasets are passed in, only keep key values
    that are shared by 2 or more datasets.
    '''
    
    # Combine all records into a single Ray dataset
    _records = []
    for idx, dataset in enumerate(records):
        processed = parse_input(dataset)
        
        for record in processed:
            new_record = {"idx": idx, "record": record}
            if key: # expose key values
                if not isinstance(record.text, dict):
                    raise ValueError("Records must be dict to use key.")
                for k in key:
                    new_record[k] = record.text.get(k, None)
            
            _records.append(new_record)
    
    ds = ray.data.from_items(_records)
    
    grouped = ds.groupby(key).aggregate(_GroupbyAggregator()).take_all()
    
    output = []
    # Format output to be
    # [{"records": [[ds1_rec1, ds1_rec2, ...], [ds2_rec1, ...] ...]}, ...]
    for group in grouped:
        result = group["__result__"]
        if len(records) == 1 or len(result) > 1:
            output.append({"records": [result[idx] for idx in result]})
    return output


def block_single_list(grouped_records: list[dict],
                      ignore: list | None = None) -> list[dict]:
    ''' Pairwise compare all records in each group. '''
    
    batch_size = parameter.batch_size()
    similarity = parameter.similarity()
    remote_tasks, batch = [], []
    
    for group in grouped_records:
        for left, right in combinations(group["records"][0], 2):
            batch.append((left, right))
            if len(batch) == batch_size:
                remote_tasks.append(
                    compare.remote((batch, ignore, similarity))
                )
                batch = []
    if len(batch) > 0:
        remote_tasks.append(
            compare.remote((batch, ignore, similarity))
        )
    
    # Use tqdm and ray.wait to show progress as tasks complete
    results = []
    pending = remote_tasks.copy()
    with tqdm(total=len(remote_tasks), 
              desc="Blocking") as pbar:
        while pending:
            done, pending = ray.wait(pending, num_returns=1)
            results.extend(ray.get(done)[0])
            pbar.update(len(done))
    
    return results


def block_across_lists(grouped_records: list[dict],
                       ignore: list | None = None) -> list[dict]:
    ''' Pairwise compare all records across different lists in each group. '''
    
    batch_size = parameter.batch_size()
    similarity = parameter.similarity()
    remote_tasks, batch = [], []
    
    for group in grouped_records:
        for sublist1, sublist2 in combinations(group["records"], 2):
            for left, right in product(sublist1, sublist2):
                batch.append((left, right))
                if len(batch) == batch_size:
                    remote_tasks.append(
                        compare.remote((batch, ignore, similarity))
                    )
                    batch = []
    if len(batch) > 0:
        remote_tasks.append(
            compare.remote((batch, ignore, similarity))
        )
    
    # Use tqdm and ray.wait to show progress as tasks complete.
    results = []
    pending = remote_tasks.copy()
    with tqdm(total=len(remote_tasks), 
              desc="Blocking") as pbar:
        while pending:
            done, pending = ray.wait(pending, num_returns=1)
            results.extend(ray.get(done)[0])
            pbar.update(len(done))
    
    return results


@ray.remote
def compare(input: tuple[list, list | None, list | None]) -> list[dict]:
    ''' Block using string similarity. '''
    
    pairs, ignore, similarity = input
    result = []
    if similarity is None:
        similarity = parameter.similarity()

    for l, r in pairs:
        # If purely image, do not compare
        if isinstance(l, _ImageRecord) or isinstance(r, _ImageRecord):
            result.append({'left': convert_to_original(l), 
                           'right': convert_to_original(r)})
        else:
            left_str = convert_to_str(l.text, ignore)
            right_str = convert_to_str(r.text, ignore)
            if fuzz.token_set_ratio(left_str, right_str) >= similarity:
                result.append({'left': convert_to_original(l), 
                            'right': convert_to_original(r)})
    
    return result


def convert_to_str(record: str | dict, ignore: list | None = None):
    match record:
        case str():
            return record
        case dict():
            if ignore:
                return ' '.join(map(str, (value for key, value in record.items() if key not in ignore)))
            else:
                return ' '.join(map(str, record.values()))
        case _:
            return str(record)


def convert_to_original(record: _Record) -> Record:
    if isinstance(record, _TextRecord):
        return record.text
    elif isinstance(record, _ImageRecord):
        return record.image
    else:
        return record


def init():
    ''' Initialize Ray. '''
    ray.init(ignore_reinit_error=True)


class _GroupbyAggregator(AggregateFnV2):
    def __init__(self):
        # Start with an empty dict mapping idx to a list of records
        super().__init__(
            name="__result__",
            zero_factory=lambda: {},
            on=None,
            ignore_nulls=False,
        )

    def aggregate_block(self, block: Any) -> dict[int, list]:
        block_acc = BlockAccessor.for_block(block)
        accumulator: dict[int, list] = {}
        
        # Read each row, group by idx
        for row in block_acc.iter_rows(public_row_format=False):
            idx = row["idx"]
            rec = row["record"]
            if idx in accumulator:
                accumulator[idx].append(rec)
            else:
                accumulator[idx] = [rec]
        
        return accumulator

    def combine(self, 
                current_accumulator: dict[int, list[dict]], 
                new: dict[int, list[dict]]) -> dict[int, list[dict]]:
        # Merge two accumulators on idx
        for list_idx, recs in new.items():
            if list_idx in current_accumulator:
                current_accumulator[list_idx].extend(recs)
            else:
                current_accumulator[list_idx] = recs
        return current_accumulator
