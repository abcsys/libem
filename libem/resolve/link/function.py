from libem.resolve.cluster.interface import cluster

schema = {}


def func(records_a, records_b):
    import pandas as pd

    assert type(records_a) == type(records_b)

    match records_a:
        case pd.DataFrame():
            df_a, df_b = records_a, records_b

            df_a["__source__"] = 0
            df_b["__source__"] = 1

            df_a, df_b = align(df_a, df_b)
            # concatenate to one dataframe
            df = pd.concat([df_a, df_b], ignore_index=True)
            # cluster the rows
            df_cluster = cluster(df.drop(columns=["__source__"]))
            # add source column back
            df_cluster = pd.concat([df_cluster, df[["__source__"]]], axis=1)
        case _:
            raise NotImplementedError

    return df_cluster


def align(df_a, df_b):
    # assume that df_a and df_b have the aligned schemas
    return df_a, df_b
