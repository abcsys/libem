import re
import duckdb
import pandas as pd

from libem.resolve.cluster.function import func as cluster_func


class DuckDBTable():
    def __init__(self, 
                 table: str | None = None, 
                 con: duckdb.DuckDBPyConnection | None = None) -> None:
        ''' Helper class to pass into libem.cluster(). '''
        
        if not con:
            self.con = duckdb.connect(":default:")
        else:
            self.con = con
        
        # get all tables in DB
        tables = self.con.sql(
                "SELECT table_name FROM INFORMATION_SCHEMA.TABLES"
            ).fetchall()
        if len(tables) == 0:
            raise ValueError("No tables in database.")
        tables = [t[0] for t in tables]
        
        # check table name exists
        if table is not None:
            if table not in tables:
                raise ValueError("Table not found in database.")
        # if name not given, assume only one table in DB
        else:
            if len(tables) > 1:
                raise ValueError("Multiple tables found, "
                                 "please specify which table to use.")
            else:
                table = tables[0]
        
        self.table = table
        
        # for assigning new table names
        self.counter = 1
    
    def get(self) -> pd.DataFrame:
        ''' Get the table. '''
        
        return self.con.execute(
                f"SELECT * FROM {self.table}"
            ).df()
    
    
    def add(self, df: pd.DataFrame) -> str:
        ''' Add results to a new table and return the table name. '''
        
        def get_new_table_name() -> str:
            ''' Generate a valid new table name to write to. '''
            
            # get all tables in DB
            tables = self.con.sql(
                    "SELECT table_name FROM INFORMATION_SCHEMA.TABLES"
                ).fetchall()
            tables = [t[0] for t in tables]
            
            new_table = self.table + "_clustered"
            
            # append number if table already exists
            if new_table in tables:
                new_table = f"{new_table}_{self.counter}"
                self.counter += 1
            while new_table in tables:
                new_table = re.sub(r'\d+$', str(self.counter), new_table)
                self.counter += 1
            
            return new_table
        
        new_table = get_new_table_name()
        
        self.con.execute(f"CREATE TABLE {new_table} AS "
                          "SELECT * FROM df")
        return new_table


def func(input: DuckDBTable, sort: bool = False) -> str:
    df = input.get()
    
    clusters = cluster_func(
            df.to_dict(orient="records")
        )
    
    df["__cluster__"] = [cluster_id for cluster_id, _ in clusters]
    
    if sort:
        df = df.sort_values(by="__cluster__")
    
    return input.add(df)
