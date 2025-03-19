from tqdm import tqdm
from typing import Iterable

import libem
from libem.struct import (
    Record, SingleRecord,
    digest
)
from libem.resolve.cluster import parameter

ClusterID = int

schema = {}


def func(*records: Iterable[Record]) -> list[(ClusterID, SingleRecord)]:
    """
    Block, match, and cluster records.
    If multiple iterables are passed in, only cluster across the iterables.

    Returns a list of tuples, each containing a cluster id and a record.
    """
    
    pairs, answers = block_and_match(*records)
    flattened_records = [record for iter in records for record in iter]
    digests = [digest(record) for record in flattened_records]

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

        if answer['answer'] == 'yes':
            if left_cluster_id == right_cluster_id:
                continue
            
            # merge the cluster with the higher id
            # into the lower id cluster when matched
            low_cluster_id = min(left_cluster_id, right_cluster_id)
            high_cluster_id = max(left_cluster_id, right_cluster_id)
            cluster_id_records[low_cluster_id].extend(
                cluster_id_records.pop(high_cluster_id)
            )
            
            for record_digest in cluster_id_records[low_cluster_id]:
                record_cluster_ids[record_digest] = low_cluster_id
        else:
            if left_cluster_id == right_cluster_id:
                # TBD: report inconsistent match results
                libem.debug(f"[cluster] inconsistent match results for pair:\n"
                            f"{libem.pformat(pair)};\nanswer: {answer}.\n"
                            f"Expected to be in the same cluster: {left_cluster_id} "
                            f"but reported unmatched, violating the transitivity "
                            f"of the same-as relation.")

    libem.debug(f"[cluster] {len(cluster_id_records)} clusters found,"
                f"average cluster size: {len(flattened_records) / len(cluster_id_records):.2f}")

    # reassign cluster ids so that they increment from 0 without gaps, 
    # the final cluster_id order will follow the input records order
    for i, cluster_id in enumerate(cluster_id_records.keys()):
        for record_digest in cluster_id_records[cluster_id]:
            record_cluster_ids[record_digest] = i
    
    return [
        (record_cluster_ids[d], r)
        for d, r in zip(digests, flattened_records)
    ]


def block_and_match(*records: Iterable[Record]) -> tuple[list[dict], list[dict]]:
    block = parameter.block_func
    match = parameter.match_func

    pairs = block(*records)
    if len(pairs) > 0:
        answers = match(pairs)
    else:
        answers = []

    return pairs, answers
