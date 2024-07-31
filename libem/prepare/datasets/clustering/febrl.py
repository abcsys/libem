import os
import pandas as pd

import libem.prepare.datasets as datasets

DIR_PATH = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH,
                        "clustering", "febrl")
TEST_FILE = os.path.join(DIR_PATH, "test.csv")


def load_test():
    df = pd.read_csv(TEST_FILE)
    df = df.drop(columns=["recId", "id"])
    return df
