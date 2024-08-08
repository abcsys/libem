from typing import (
    Union, Iterator,
    TYPE_CHECKING
)

from libem.resolve.cluster.function import func

if TYPE_CHECKING:
    import pandas as pd

InputType = Union[
    Iterator[str],
    Iterator[dict],
    "pd.DataFrame",
]

ID = int

OutputType = Union[
    list[(ID, str)],
    list[(ID, dict)],
    "pd.DataFrame",
]


def cluster(records: InputType, *, sort=False) -> OutputType:
    import pandas as pd

    match records:
        case pd.DataFrame():
            from libem.resolve.cluster.integrations.pandas import func as pandas_func

            if sort:
                return pandas_func(records).sort_values(by="__cluster__")
            else:
                return pandas_func(records)
        case _:
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
