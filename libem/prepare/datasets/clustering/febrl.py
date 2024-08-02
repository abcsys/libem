import os

import libem.prepare.datasets as datasets

DIR_PATH = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH,
                        "clustering", "febrl")
TEST_FILE = os.path.join(DIR_PATH, "test.csv")


def load_test(num_samples=-1):
    import pandas as pd
    
    df = pd.read_csv(TEST_FILE)
    df = df.drop(columns=["recId", "id"])
    if num_samples > 0:
        return df[:num_samples]
    else:
        return df


def load_raw(num_samples=-1):
    df = load_test(num_samples)
    df = df.drop(columns=["cluster_id"])
    df = df.sample(frac=1).reset_index(drop=True)
    return df
