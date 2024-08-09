import pprint
import random
import pymongo

import libem
from libem.prepare.datasets.clustering import febrl
from libem.resolve.cluster.integrations.mongodb import MongoCollection

def main():
    random.seed(1)
    num_samples = 5
    
    # create test db + collection
    client = pymongo.MongoClient()
    with pymongo.timeout(1):
        try:
            client.admin.command('ping') 
        except:
            print("Error: Failed to ping server. "
                "Make sure a local instance of MongoDB is running.")
            return
    
    db_names = client.list_database_names()
    test_db = get_available_name('test', db_names)
    test = client[test_db]['test']
    
    # add dataset to test collection
    load_sample(num_samples, test)
    print(f"Before clustering, from collection: {test_db}.test")
    pprint.pprint(list(test.find({}, {
        '_id': 0, 'fName': 1, 'lName': 1, 
        'street': 1, 'dob': 1, 'ssn': 1
    })), sort_dicts=False)
    
    # run cluster using the MongoCollection helper
    results = libem.cluster(MongoCollection(client[test_db], 'test'), sort=True)
    print(f"After clustering, from collection: {test_db}.{results}")
    pprint.pprint(list(client[test_db][results].find({}, {
        '_id': 0, 'fName': 1, 'lName': 1, 
        'street': 1, 'dob': 1, 'ssn': 1, '__cluster__': 1
    })), sort_dicts=False)
    
    # delete test DB
    client.drop_database(test_db)
    
    
def load_sample(num_samples, collection):
    ''' Load a sample from the febrl dataset into mongodb. '''
    
    # load in dataset and remove cluster_id
    df = febrl.load_test() \
        .head(num_samples) \
        .sample(frac=1) \
        .reset_index(drop=True)
    df_test = df.drop(["cluster_id"], axis=1)
    
    collection.insert_many(df_test.to_dict(orient='records'))


def get_available_name(basename, names) -> str:
    ''' Generate a valid new name to write to. '''
    
    # append number if table already exists
    if basename in names:
        index = 1
        while f"{basename}_{index}" in names:
            index += 1
    
        return f"{basename}_{index}"
    return basename


if __name__ == '__main__':
    main()
