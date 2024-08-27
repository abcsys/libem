import os
import time
import pandas as pd

import benchmark as bm
from benchmark.suite.util import (
    run_benchmark, report_to_dataframe, 
    tabulate, plot, save, show
)

name = os.path.basename(__file__).replace(".py", "").replace('_', '-')


def run(args):
    if args.plot:
        files = list(os.scandir(bm.result_dir))
        for file in reversed(files):
            if file.name[26:-4] == name:
                print(f"Plotting run: {file.name}")
                plot(file)
                return
        
        print(f"Could not find past {name} suite results to plot.")
        return
    
    benchmarks = bm.classic_benchmarks.keys()

    args.block = False
    args.match = True
    args.model = "gpt-4o-mini"
    args.num_pairs = -1
    
    # do not use downstream log/print
    args.log = False
    args.quiet = True
    
    print(f"Benchmark: Running all {len(benchmarks)} benchmarks "
          f"with {args.model}:")
    start = time.time()

    reports = {}
    for benchmark in benchmarks:
        report = run_benchmark(benchmark, args)
        reports[benchmark] = report["stats"]["match"]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")

    df = report_to_dataframe(reports)
    file_name = save(df, name)

    # generate markdown table
    df["pairs_per_$"] = df["num_pairs"] // df["cost"]
    df = df[["benchmark", "precision", "recall", "f1",
             "cost", "pairs_per_$", "throughput"]]
    
    # add column-wise average
    mean = df[["precision", "recall", "f1",
               "cost", "pairs_per_$", "throughput"]].mean()
    mean["benchmark"] = "Average"
    df = pd.concat([df, mean.to_frame().T])
    
    field_names = {
        "benchmark": "Benchmark",
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1",
        "cost": "Cost ($)",
        "pairs_per_$": "Pairs per $",
        "throughput": "Throughput (pps)",
    }
    df = df.rename(columns=field_names)
    
    tabulate(df, name)
    plot(file_name)
    show(df)

    return reports
