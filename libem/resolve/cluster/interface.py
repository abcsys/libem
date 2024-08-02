import pandas as pd
from typing import Union, Iterator

from libem.resolve.cluster.function import func
from libem.resolve.cluster.integrations.pandas import func as pandas_func

InputType = Union[
    Iterator[str],
    Iterator[dict],
    pd.DataFrame
]

OutputType = Union[
    list[(int, str)],
    list[(int, dict)],
    pd.DataFrame,
]


def cluster(records: InputType, sort=False) -> OutputType:
    match records:
        case pd.DataFrame():
            # add a column of 'cluster_id' to the DataFrame
            if sort:
                return pandas_func(records).sort_values(by="cluster_id")
            else:
                return pandas_func(records)
        case _:
            # return a list of clusters
            if sort:
                return sorted(func(records), key=lambda x: x[0])
            else:
                return func(records)


def eval(truths: list[int], preds: list[int]) -> dict:
    import sklearn.metrics as metrics

    return {
        "adjusted_rand_score": metrics.adjusted_rand_score(truths, preds),
        "adjusted_mutual_info_score": metrics.adjusted_mutual_info_score(truths, preds),
        "homogeneity_score": metrics.homogeneity_score(truths, preds),
        "completeness_score": metrics.completeness_score(truths, preds),
    }
