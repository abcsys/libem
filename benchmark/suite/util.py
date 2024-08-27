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
    output_file = os.path.join(
                    bm.table_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    f"suite-{name}.md")
    
    df.to_markdown(output_file, index=False)
    
    print(f"Markdown table saved to: {output_file}")


def plot(file: str, x_axis: str = 'benchmark'):
    import seaborn as sns
    from matplotlib import pyplot as plt
    
    df = pd.read_csv(file)
    sns.set_theme(font_scale=1.3)
    sns.barplot(df, x=x_axis, y='f1', color='#2ecc71', width=0.7)
    plt.xticks(rotation=90)
    plt.ylim(0, 100)
    plt.title('')
    plt.xlabel('')
    plt.ylabel("F1 Score (%)")
    
    output_file = os.path.join(
                    bm.figure_dir,
                    f"{os.path.basename(file)[:-4]}.svg")
    plt.savefig(output_file, format='svg', bbox_inches = "tight")
    
    print(f"Plot saved to: {output_file}")


def save(df: pd.DataFrame, name: str):
    output_file = os.path.join(
                    bm.result_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    f"suite-{name}.csv")
    
    df.to_csv(output_file, index=False)
    
    print(f"Results saved to: {output_file}")
    
    return output_file


def show(df: pd.DataFrame):
    print(df.to_string(index=False))
