import pandas as pd

from libem.resolve.cluster.function import func as cluster_func

schema = {
    "type": "function",
    "function": {
        "name": "cluster",
        "description": "Perform the clustering stage of "
                       "entity matching given a dataframe "
                       "and add a __cluster__ column.",
        "parameters": {
            "type": "object",
            "properties": {
                "df": {
                    "type": "dataframe",
                    "description": "A pandas DataFrame containing the dataset.",
                },
            },
            "required": ["df"],
        },
    }
}


def cluster(*args, **kwargs):
    return func(*args, **kwargs)


def func(df: pd.DataFrame, sort: bool = False) -> pd.DataFrame:
    clusters = cluster_func(
        df.to_dict(orient="records")
    )

    new_df = df.copy()
    new_df["__cluster__"] = [cluster_id for cluster_id, _ in clusters]

    if sort:
        return new_df.sort_values(by="__cluster__")

    return new_df
