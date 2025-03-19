import builtins

from libem.resolve.cluster.interface import cluster

schema = {}


def func(*records):
    import pandas as pd

    first_type = type(records[0])
    for record in records:
        assert type(record) == first_type

    match first_type:
        case pd.DataFrame:
            # keep track of the source ids
            source_ids = []
            for i, df in enumerate(records):
                source_ids.extend([i] * len(df))
            
            dfs = align(*records)
            
            # cluster the rows
            df_cluster = cluster(*dfs)
            
            # add source column back
            df_cluster = pd.concat([df_cluster, pd.Series(source_ids, name="__source__")], axis=1)
        case builtins.list:
            # convert all record lists to dataframes
            dfs = [pd.DataFrame(record) for record in records]
            return func(*dfs)
        case _:
            raise NotImplementedError

    return df_cluster


def align(*dfs):
    # assume that all dfs have aligned schemas
    return dfs
