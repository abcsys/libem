def load(num_samples=-1):
    from recordlinkage.datasets import load_febrl4

    df_a, df_b = load_febrl4()
    df_a = prepare(df_a, num_samples)
    df_b = prepare(df_b, num_samples)

    return df_a, df_b


def prepare(df, num_samples=-1):
    """
    Ensures the returned dataframes contain the pairs of records to be linked.
    """
    num_samples = num_samples if num_samples > 0 else len(df)
    df = df.reset_index()

    df['numeric_id'] = df['rec_id'].str.extract('(\d+)').astype(int)
    df = df.sort_values('numeric_id').reset_index(drop=True)
    df = df.drop(columns=['numeric_id'])[:num_samples]

    return df.sample(frac=1).reset_index(drop=True)
