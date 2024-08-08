import libem

schema = {}


def func(records):
    import pandas as pd

    match records:
        case pd.DataFrame():
            if "cluster_id" not in records.columns:
                libem.info("[dedupe] __cluster__ not found in records, "
                           "do clustering first")
                records: pd.DataFrame = libem.cluster(records)
                return records.drop_duplicates("__cluster__", keep="first") \
                    .drop("__cluster__", axis=1).reset_index(drop=True)

            return records.drop_duplicates("__cluster__", keep="first") \
                .reset_index(drop=True)
        case list():
            if "cluster_id" not in records[0]:
                libem.info("[dedupe] __cluster__ not found in records, "
                           "do clustering first")
                records = libem.cluster(records)
                return list({record[0]: record for record in records}.values())

            return list({record[0]: record for record in records}.values())
        case _:
            raise NotImplementedError(f"Unsupported type: {type(records)}")
