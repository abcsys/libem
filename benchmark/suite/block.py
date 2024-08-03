import os
import time

import libem
import benchmark.run
from benchmark.classic import dataset_benchmarks, block_similarities
from benchmark.suite.util import (report_to_dataframe, 
                                  tabulate, plot, 
                                  save, show)

name = os.path.basename(__file__).replace(".py", "")


def run(args):
    datasets = dataset_benchmarks.keys()

    args.block = True
    args.match = False
    args.num_pairs = -1

    # do not use downstream log/print
    log = args.log
    args.log = False
    quiet = args.quiet
    args.quiet = True

    print(f"Benchmark: Blocking all {len(datasets)} datasets:")
    start = time.time()

    reports = {}
    for dataset in datasets:
        args.name = dataset

        libem.reset()
        report = benchmark.run.run(args)
        reports[dataset] = report["stats"]["block"]
        reports[dataset]["similarity_cutoff"] = block_similarities[dataset]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")
    
    df = report_to_dataframe(reports)
    if log:
        save(df, name)
    
    # generate markdown table
    df = df[["dataset", "similarity_cutoff", "percent_blocked", "f1", "throughput"]]
    field_names = {
        "dataset": "Dataset",
        "total_pairs": "Total Pairs",
        "similarity_cutoff": "Similarity Cutoff (0-100)",
        "percent_blocked": "Percent Blocked",
        "f1": "F1",
        "throughput": "Throughput (pps)",
    }
    df = df.rename(columns=field_names)
    
    if log:
        tabulate(df, name)
    
    if not quiet:
        plot(df)
        show(df)

    return reports
