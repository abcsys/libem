import os
import time

import libem
import benchmark.run
from benchmark.classic import dataset_benchmarks
from benchmark.suite.util import (report_to_dataframe, 
                                  tabulate, plot, 
                                  save, show)

name = os.path.basename(__file__).replace(".py", "")


def run(args):
    datasets = dataset_benchmarks.keys()

    args.block = False
    args.match = True
    args.model = "gpt-4-turbo"
    args.num_pairs = -1
    
    # do not use downstream log/print
    log = args.log
    args.log = False
    quiet = args.quiet
    args.quiet = True
    
    print(f"Benchmark: Matching all {len(datasets)} datasets "
          f"with {args.model}:")
    start = time.time()

    reports = {}
    for dataset in datasets:
        args.name = dataset

        libem.reset()
        report = benchmark.run.run(args)
        reports[dataset] = report["stats"]["match"]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")

    df = report_to_dataframe(reports)
    if log:
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
    
    if log:
        tabulate(df, name)
    
    if not quiet:
        plot(df)
        show(df)

    return reports
