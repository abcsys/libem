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


def func(*dfs: pd.DataFrame, sort: bool = False) -> pd.DataFrame:
    clusters = cluster_func(
        *[df.to_dict(orient="records") for df in dfs]
    )
    print(clusters)
    
    rows = []
    for cluster_id, record in clusters:
        row = record.copy()
        row["__cluster__"] = cluster_id
        rows.append(row)
    new_df = pd.DataFrame(rows)

    if sort:
        return new_df.sort_values(by="__cluster__")

    return new_df
