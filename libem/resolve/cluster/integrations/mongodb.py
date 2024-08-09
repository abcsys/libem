import bson
import pymongo.database

from libem.resolve.cluster.function import func as cluster_func


class Collection:
    def __init__(self,
                 db_name: str,
                 name: str,
                 client: pymongo.MongoClient = None,
                 ) -> None:
        self.name = name
        self.db_name = db_name
        self.client = self.connect() if client is None else client

        if self.db_name not in self.client.list_database_names():
            raise ValueError(f"Database {self.db_name} not found.")
        self.db = self.client[self.db_name]

        if not self.exist():
            raise ValueError(
                f"Collection {self.name} "
                f"not found in database {self.db_name}."
            )

    def __call__(self, collection: list = None):
        if collection is None:
            return self.load()
        else:
            return self.replace(collection)

    def connect(self):
        self.client = pymongo.MongoClient()
        with pymongo.timeout(1):
            try:
                self.client.admin.command('ping')
            except:
                print("Error: Failed to ping server. "
                      "Make sure a local instance of MongoDB is running.")
                raise Exception("Failed to connect to MongoDB.")
        return self.client

    def exist(self):
        return self.name in self.db.list_collection_names()

    def load(self) -> list:
        return list(self.db[self.name].find({}))

    def replace(self, collection: list):
        session = self.client.start_session()
        with session.start_transaction():
            try:
                self.db[self.name].drop()
                self.db[self.name].insert_many(collection)
                session.commit_transaction()
            except Exception as e:
                session.abort_transaction()
                raise e
        return self


def cluster(*args, **kwargs):
    return func(*args, **kwargs)


def func(coll: Collection, sort: bool = False) -> Collection:
    docs = decode_id(coll())
    clusters = cluster_func(docs)

    if sort:
        clusters = sorted(clusters, key=lambda x: x[0])

    return coll(encode_id([
        {
            "__cluster__": id,
            **doc
        } for id, doc in clusters
    ]))


def decode_id(docs: list) -> list:
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return docs


def encode_id(docs: list) -> list:
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = bson.ObjectId(doc["_id"])
    return docs
