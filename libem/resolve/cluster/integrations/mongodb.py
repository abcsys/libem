import pymongo.database

from libem.resolve.cluster.function import func as cluster_func


class MongoCollection():
    def __init__(self, 
                 db: pymongo.database.Database, 
                 collection: str | None = None) -> None:
        ''' Helper class to pass into libem.cluster(). '''
        
        self.db = db
        
        # get all collections in DB
        collections = self.db.list_collection_names()
        if len(collections) == 0:
            raise ValueError("No collections in database.")
        
        # check collection name exists
        if collection is not None:
            if collection not in collections:
                raise ValueError("Collection not found in database.")
        # if name not given, assume only one collection in DB
        else:
            if len(collections) > 1:
                raise ValueError("Multiple collections found, "
                                 "please specify which collection to use.")
            else:
                collection = collections[0]
        
        self.collection = collection
    
    
    def get(self) -> list:
        ''' Get the collection. '''
        
        return self.db[self.collection].find({}, {'_id': False})
    
    
    def add(self, data: list) -> str:
        ''' Add results to a new collection and return the collection name. '''
        
        def get_new_collection_name() -> str:
            ''' Generate a valid new collection name to write to. '''
            
            collections = self.db.list_collection_names()
            
            basename = self.collection + "_clustered"
            
            # append number if collection already exists
            if basename in collections:
                counter = 1
                while f"{basename}_{counter}" in collections:
                    counter += 1
                
                return f"{basename}_{counter}"
            return basename
        
        new_collection = get_new_collection_name()
        
        self.db[new_collection].insert_many(data)
        return new_collection


def func(input: MongoCollection, sort: bool = False) -> str:
    clusters = cluster_func(input.get())
    
    if sort:
        clusters = sorted(clusters, key=lambda x: x[0])
    
    collection = [{
            "__cluster__": id,
            **rec
        } for id, rec in clusters]
    
    return input.add(collection)
