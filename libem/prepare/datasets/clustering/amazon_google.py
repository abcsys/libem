import os

import libem.prepare.datasets as datasets

DIR_PATH = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH,
                        "clustering", "amazon-google")
TEST_FILE = os.path.join(DIR_PATH, "test.ndjson")


def load_test(num_samples=-1):
    import pandas as pd
    
    df = pd.read_json(TEST_FILE, lines=True)
    if num_samples > 0:
        return df[:num_samples]
    else:
        return df


def load_raw(num_samples=-1):
    df = load_test(num_samples)
    df = df.drop(columns=["cluster_id"])
    df = df.sample(frac=1).reset_index(drop=True)
    return df
