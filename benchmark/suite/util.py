import copy
import os
import pandas as pd
from datetime import datetime

import libem
import benchmark as bm


def run_benchmark(benchmark: str, args):
    libem.reset()
    
    _args = copy.deepcopy(args)
    _args.name = benchmark
    benchmark = bm.benchmarks[benchmark]
    
    return benchmark(_args)


def report_to_dataframe(reports, key_col: str = "benchmark"):
    rows = []
    for key, report in reports.items():
        # flatten report dict
        df = pd.json_normalize(report, sep=' ')
        # rename to only use leaf key
        df = df.rename(columns={k: k.split()[-1] for k in df.columns})
        # add benchmark column
        df.insert(0, key_col, [key])
        rows.append(df)

    return pd.concat(rows)


def tabulate(df: pd.DataFrame, name: str):
    name = name.replace('_', '-')
    output_file = os.path.join(
                    bm.table_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    f"suite-{name}.md")
    
    df.to_markdown(output_file, index=False)
    
    print(f"Markdown table saved to: {output_file}")


def plot(df: pd.DataFrame):
    pass


def save(df: pd.DataFrame, name: str):
    name = name.replace('_', '-')
    output_file = os.path.join(
                    bm.result_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    f"suite-{name}.csv")
    
    df.to_csv(output_file, index=False)
    
    print(f"Results saved to: {output_file}")


def show(df: pd.DataFrame):
    print(df.to_string(index=False))
