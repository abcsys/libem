import builtins
import libem

schema = {}


def func(*records):
    import pandas as pd
    
    first_type = type(records[0])
    for record in records:
        assert type(record) == first_type

    match first_type:
        case pd.DataFrame:
            records: pd.DataFrame = libem.cluster(*records)
            return records.drop_duplicates("__cluster__", keep="first") \
                .drop("__cluster__", axis=1).reset_index(drop=True)
        case builtins.list:
            records: list[tuple] = libem.cluster(*records)
            
            deduped = {}
            for cluster_id, record in records:
                if cluster_id not in deduped:
                    deduped[cluster_id] = record
            
            return deduped.values()
        case _:
            raise NotImplementedError(f"Unsupported type: {type(records)}")
