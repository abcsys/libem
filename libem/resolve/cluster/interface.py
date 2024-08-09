from typing import (
    Union, Iterator,
    TYPE_CHECKING
)

from libem.resolve.cluster.function import func

if TYPE_CHECKING:
    import pandas as pd
    from libem.resolve.cluster.integrations import duckdb
    from libem.resolve.cluster.integrations import mongodb

InputType = Union[
    Iterator[str],
    Iterator[dict],
    "pd.DataFrame",
    "duckdb.Table",
    "mongodb.Collection",
]

ID = int

OutputType = Union[
    list[(ID, str)],
    list[(ID, dict)],
    "pd.DataFrame",
    "duckdb.Table",
    "mongodb.Collection",
]


def cluster(records: InputType, *, sort=False) -> OutputType:
    import pandas as pd

    from libem.resolve.cluster.integrations import pandas
    from libem.resolve.cluster.integrations import duckdb
    from libem.resolve.cluster.integrations import mongodb

    match records:
        case pd.DataFrame():
            return pandas.cluster(records, sort)
        case duckdb.Table():
            return duckdb.cluster(records, sort)
        case mongodb.Collection():
            return mongodb.cluster(records, sort)
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
