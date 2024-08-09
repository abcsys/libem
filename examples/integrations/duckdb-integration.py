import random
import duckdb

import libem
from libem.prepare.datasets.clustering import febrl
from libem.resolve.cluster.integrations.duckdb import DuckDBTable

def main():
    random.seed(1)
    num_samples = 10
    
    # add dataset to duckdb
    load_sample(num_samples)
    print("Before clustering, showing table: test")
    print(duckdb.sql("SELECT * FROM test"))
    
    # run cluster using the DuckDBTable helper
    new_table_name = libem.cluster(DuckDBTable(), sort=True)
    print("After clustering, showing table:", new_table_name)
    print(duckdb.sql(f"SELECT * FROM {new_table_name}"))


def load_sample(num_samples):
    ''' Load a sample from the febrl dataset into duckdb. '''
    
    df = febrl.load_test() \
        .head(num_samples) \
        .sample(frac=1) \
        .reset_index(drop=True)
    df_test = df.drop(["cluster_id"], axis=1)
    
    duckdb.sql("CREATE TABLE test AS SELECT * FROM df_test")


if __name__ == '__main__':
    main()
