import libem

schema = {}


def func(records):
    import pandas as pd

    match records:
        case pd.DataFrame():
            if "cluster_id" not in records.columns:
                libem.info("[dedupe] cluster_id not found in records, "
                           "do clustering first")
                records: pd.DataFrame = libem.cluster(records)
            return records.drop_duplicates("cluster_id", keep="first")
        case list():
            return list({record["cluster_id"]: record for record in records}.values())
        case _:
            raise NotImplementedError(f"Unsupported type: {type(records)}")
