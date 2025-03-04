from typing import (
    Union, Iterator,
    TYPE_CHECKING
)

from libem.struct import SingleRecord
from libem.resolve.cluster.function import func

if TYPE_CHECKING:
    import pandas as pd
    from libem.resolve.cluster.integrations import duckdb
    from libem.resolve.cluster.integrations import mongodb

InputType = Union[
    Iterator[SingleRecord],
    "pd.DataFrame",
    "duckdb.Table",
    "mongodb.Collection",
]

ID = int

OutputType = Union[
    list[(ID, SingleRecord)],
    "pd.DataFrame",
    "duckdb.Table",
    "mongodb.Collection",
]


def cluster(*records: InputType, sort=False) -> OutputType:
    import pandas as pd

    from libem.resolve.cluster.integrations import pandas
    from libem.resolve.cluster.integrations import duckdb
    from libem.resolve.cluster.integrations import mongodb
    
    first_type = type(records[0])
    for record in records:
        assert type(record) == first_type
    
    match first_type:
        case pd.DataFrame:
            return pandas.cluster(*records, sort=sort)
        case duckdb.Table:
            if len(records) > 1:
                raise NotImplementedError
            return duckdb.cluster(records[0], sort=sort)
        case mongodb.Collection:
            if len(records) > 1:
                raise NotImplementedError
            return mongodb.cluster(records[0], sort=sort)
        case _:
            if sort:
                return sorted(func(*records), key=lambda x: x[0])
            else:
                return func(*records)


def eval(truths: list[int], preds: list[int]) -> dict:
    import sklearn.metrics as metrics

    return {
        "adjusted_rand_score": metrics.adjusted_rand_score(truths, preds),
        "adjusted_mutual_info_score": metrics.adjusted_mutual_info_score(truths, preds),
        "homogeneity_score": metrics.homogeneity_score(truths, preds),
        "completeness_score": metrics.completeness_score(truths, preds),
    }
