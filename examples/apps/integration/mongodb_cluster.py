import pprint
import random
import pymongo

import libem
from libem.prepare.datasets.clustering import febrl
from libem.resolve.cluster.integrations.mongodb import Collection

client = pymongo.MongoClient()


def main():
    random.seed(1)
    num_samples = 10

    load_febrl(num_samples)
    print(f"Before clustering:")
    pprint.pprint(
        list(client["biodb"]["febrl"].find({})),
        sort_dicts=False,
    )
    
    libem.cluster(
        Collection("biodb", "febrl"), sort=True,
    )

    print(f"After clustering: ")
    pprint.pprint(
        list(client["biodb"]["febrl"].find({})),
        sort_dicts=False
    )

    client.drop_database("biodb")


def load_febrl(num_samples):
    df = febrl.load_test() \
        .head(num_samples) \
        .sample(frac=1) \
        .reset_index(drop=True)
    df_test = df.drop(["cluster_id"], axis=1)

    coll = client["biodb"]["febrl"]
    coll.insert_many(df_test.to_dict(orient='records'))


if __name__ == '__main__':
    main()
