import os
import time

from benchmark.classic import dataset_benchmarks
from benchmark.suite.util import (run_dataset, 
                                  report_to_dataframe, 
                                  tabulate, plot, 
                                  save, show)

name = os.path.basename(__file__).replace(".py", "")


def run(args):
    datasets = dataset_benchmarks.keys()

    args.block = False
    args.match = True
    args.model = "gpt-4o-mini"
    args.num_pairs = -1
    
    # do not use downstream log/print
    args.log = False
    args.quiet = True
    
    print(f"Benchmark: Matching all {len(datasets)} datasets "
          f"with {args.model}:")
    start = time.time()

    reports = {}
    for dataset in datasets:
        report = run_dataset(dataset, args)
        reports[dataset] = report["stats"]["match"]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")

    df = report_to_dataframe(reports)
    save(df, name)

    # generate markdown table
    df = df[["dataset", "precision", "recall", "f1",
             "cost", "throughput"]]
    field_names = {
        "dataset": "Dataset",
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1",
        "cost": "Cost ($)",
        "throughput": "Throughput (pps)",
    }
    df = df.rename(columns=field_names)
    
    tabulate(df, name)
    plot(df)
    show(df)

    return reports
