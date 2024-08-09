import random
import duckdb

import libem
from libem.prepare.datasets.clustering import febrl

from libem.resolve.cluster.integrations.duckdb import Table


def main():
    random.seed(1)
    num_samples = 10
    load_febrl(num_samples)

    print("Before clustering:")
    print(duckdb.sql("SELECT * FROM febrl"))

    libem.cluster(
        Table("febrl"), sort=True
    )

    print("After clustering:")
    print(duckdb.sql(f"SELECT * FROM febrl"))


def load_febrl(num_samples):
    df = febrl.load_test() \
        .head(num_samples) \
        .sample(frac=1) \
        .reset_index(drop=True)
    df_test = df.drop(["cluster_id"], axis=1)

    duckdb.sql("CREATE TABLE febrl AS SELECT * FROM df_test")


if __name__ == '__main__':
    main()
