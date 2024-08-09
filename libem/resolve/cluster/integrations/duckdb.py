import duckdb
import pandas as pd

from libem.resolve.cluster.function import func as cluster_func


class Table:
    def __init__(
            self,
            name: str,
            conn: duckdb.DuckDBPyConnection = None
    ):
        self.name = name
        self.conn = duckdb.connect(":default:") if conn is None else conn
        if not self.exist():
            raise ValueError(f"Table {self.name} not found in database.")

    def __call__(self, df: pd.DataFrame = None):
        if df is None:
            return self.load()
        else:
            return self.replace(df)

    def exist(self):
        tables = self.conn.execute(
            "SELECT table_name "
            "FROM INFORMATION_SCHEMA.TABLES"
        ).fetchdf()['table_name'].tolist()
        return self.name in tables

    def load(self) -> pd.DataFrame:
        return self.conn.execute(
            f"SELECT * FROM {self.name}"
        ).df()

    def replace(self, df: pd.DataFrame):
        try:
            self.conn.begin()
            self.conn.execute(f"DROP TABLE IF EXISTS {self.name}")
            self.conn.execute(
                f"CREATE TABLE {self.name} AS SELECT * FROM df",
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        return self


def cluster(*args, **kwargs):
    return func(*args, **kwargs)


def func(table: Table, sort: bool = False) -> Table:
    df = table()

    clusters = cluster_func(df.to_dict(orient="records"))
    df["__cluster__"] = [cluster_id for cluster_id, _ in clusters]

    if sort:
        df = df.sort_values(by="__cluster__")

    return table(df)
