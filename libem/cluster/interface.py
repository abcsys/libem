import pandas as pd
from typing import Union, Iterator
import sklearn.metrics as metrics

from libem.cluster.function import func
from libem.cluster.integrations.pandas import func as pandas_func

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


def cluster(records: InputType) -> OutputType:
    match records:
        case pd.DataFrame():
            # add a column of 'cluster_id' to the DataFrame
            return pandas_func(records)
        case _:
            # return a list of clusters
            return func(records)


def eval(truths: list[int], preds: list[int]) -> dict:
    return {
        "adjusted_rand_score": metrics.adjusted_rand_score(truths, preds),
        "adjusted_mutual_info_score": metrics.adjusted_mutual_info_score(truths, preds),
        "homogeneity_score": metrics.homogeneity_score(truths, preds),
        "completeness_score": metrics.completeness_score(truths, preds),
    }
