import os
import time

import benchmark as bm
from benchmark.suite.util import (
    run_benchmark, report_to_dataframe, 
    tabulate, plot, save, show
)

name = os.path.basename(__file__).replace(".py", "")


def run(args):
    benchmarks = bm.benchmarks.keys()

    args.block = False
    args.match = True
    args.model = "gpt-4-turbo"
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
    save(df, name)

    # generate markdown table
    df = df[["benchmark", "precision", "recall", "f1",
             "cost", "throughput"]]
    field_names = {
        "benchmark": "Benchmark",
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
