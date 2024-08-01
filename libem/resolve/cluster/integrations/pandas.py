import pandas as pd

from libem.resolve.cluster.function import func as cluster_func

schema = {
    "type": "function",
    "function": {
        "name": "cluster",
        "description": "Perform the clustering stage of "
                       "entity matching given a dataframe "
                       "and add a cluster_id column.",
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


def func(df: pd.DataFrame) -> pd.DataFrame:
    clusters = cluster_func(
        df.to_dict(orient="records")
    )

    new_df = df.copy()
    new_df["cluster_id"] = [cluster_id for cluster_id, _ in clusters]
    return new_df
