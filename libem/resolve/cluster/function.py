import json
import hashlib
from tqdm import tqdm
from typing import Iterable

import libem
from libem.resolve.cluster import parameter

ClusterID = int
Record = str | dict

schema = {}


def func(records: Iterable[Record]) -> list[(ClusterID, Record)]:
    """
    Block, match, and cluster records.

    Returns a list of tuples, each containing a cluster id and a record.
    """
    records = list(records)
    pairs, answers = block_and_match(records)
    digests = [digest(record) for record in records]

    record_cluster_ids = {
        d: i for i, d in enumerate(digests)
    }
    cluster_id_records = {
        v: [k] for k, v in record_cluster_ids.items()
    }

    for answer, pair in tqdm(zip(answers, pairs), total=len(answers), desc="Clustering"):
        left, right = digest(pair['left']), digest(pair['right'])
        left_cluster_id = record_cluster_ids[left]
        right_cluster_id = record_cluster_ids[right]

        # merge with the smaller cluster id when matched
        if answer['answer'] == 'yes':
            if left_cluster_id == right_cluster_id:
                continue
            cluster_id = min(left_cluster_id, right_cluster_id)
            if left_cluster_id == cluster_id:
                cluster_id_records[cluster_id].extend(
                    cluster_id_records.pop(right_cluster_id)
                )
            else:
                cluster_id_records[cluster_id].extend(
                    cluster_id_records.pop(left_cluster_id)
                )
            for record_digest in cluster_id_records[cluster_id]:
                record_cluster_ids[record_digest] = cluster_id
        else:
            if left_cluster_id == right_cluster_id:
                # TBD: report inconsistent match results
                libem.debug(f"[cluster] inconsistent match results for pair:\n"
                            f"{libem.pformat(pair)};\nanswer: {answer}.\n"
                            f"Expected to be in the same cluster: {left_cluster_id} "
                            f"but reported unmatched, violating the transitivity "
                            f"of the same-as relation.")

    libem.debug(f"[cluster] {len(cluster_id_records)} clusters found,"
                f"average cluster size: {len(records) / len(cluster_id_records):.2f}")

    # add cluster id to records
    # remap cluster ids to increment from 0 without gaps
    unique_cluster_ids = sorted(
        id for id in set(record_cluster_ids.values())
    )
    remap_cluster_id = {
        old_id: new_id
        for new_id, old_id in enumerate(unique_cluster_ids)
    }
    return [
        (remap_cluster_id[record_cluster_ids[d]], r)
        for r, d in zip(records, digests)
    ]


def block_and_match(records: Iterable[Record]) -> (list, list[dict]):
    block = parameter.block_func
    match = parameter.match_func

    pairs = list(block(records))
    answers = list(match(pairs))

    return pairs, answers


def digest(record: Record) -> str:
    match record:
        case str():
            return hashlib.md5(record.encode()).hexdigest()
        case dict():
            return hashlib.md5(
                json.dumps(
                    record, sort_keys=True
                ).encode()).hexdigest()
        case _:
            return hashlib.md5(str(record).encode()).hexdigest()
