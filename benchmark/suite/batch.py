import os
import time

import benchmark as bm
from benchmark.suite.util import (
    run_benchmark, report_to_dataframe, 
    tabulate, plot, save, show
)

name = os.path.basename(__file__).replace(".py", "")


def run(args):
    if args.plot:
        files = list(os.scandir(bm.result_dir))
        for file in reversed(files):
            if file.name[26:31] == name:
                print(f"Plotting run: {file.name}")
                plot(file, x_axis="batch_size")
                return
        
        print(f"Could not find past {name} suite results to plot.")
        return
    
    args.block = False
    args.match = True
    args.num_pairs = -1
    
    # do not use downstream log/print
    args.log = False
    args.quiet = True
    
    batch_sizes = [1, 4, 16, 64, 128, 256, 512]
    
    print(f"Benchmark: Varying the batch size on the {args.name} benchmarks:")
    start = time.time()
    
    reports = {}
    for batch_size in batch_sizes:
        args.batch_size = batch_size

        report = run_benchmark(args.name, args)
        reports[batch_size] = report["stats"]["match"]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")
    
    df = report_to_dataframe(reports, key_col="batch_size")
    file_name = save(df, f"{name}-{args.name}")

    # generate markdown table
    df = df[["batch_size", "f1", "latency", "per_pair_latency",
             "cost", "throughput"]]
    field_names = {
        "batch_size": "Batch Size",
        "f1": "F1",
        "latency": "Latency",
        "per_pair_latency": "Per Pair Latency",
        "cost": "Cost ($)",
        "throughput": "Throughput (pps)",
    }
    df = df.rename(columns=field_names)

    tabulate(df, f"{name}-{args.name}")
    plot(file_name, x_axis="batch_size")
    show(df)

    return reports
