import os
import pandas as pd
from datetime import datetime

import benchmark as bm


def report_to_dataframe(reports, key_col: str = "dataset"):
    rows = []
    for key, report in reports.items():
        # flatten report
        df = pd.json_normalize(report, sep=' ')
        # rename keys
        df = df.rename(columns={k: k.split()[-1] for k in df.columns})
        # add dataset column
        df.insert(0, key_col, [key])
        rows.append(df)

    return pd.concat(rows)


def tabulate(df: pd.DataFrame, name):
    output_file = os.path.join(
                    bm.table_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    f"suite-{name}.md")
    
    df.to_markdown(output_file, index=False)
    
    print(f"Benchmark: Markdown table saved to: {output_file}")


def plot(df: pd.DataFrame):
    pass


def save(df: pd.DataFrame, name):
    output_file = os.path.join(
                    bm.result_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    f"suite-{name}.csv")
    
    df.to_csv(output_file, index=False)
    
    print(f"Benchmark: Results saved to: {output_file}")


def show(df: pd.DataFrame):
    print(df.to_string(index=False))