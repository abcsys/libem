import os
import time

import benchmark as bm
from benchmark.classic import block_similarities
from benchmark.suite.util import (
    run_benchmark, report_to_dataframe, 
    tabulate, plot, save, show
)

name = os.path.basename(__file__).replace(".py", "")


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

    args.block = True
    args.match = False
    args.num_pairs = -1

    # do not use downstream log/print
    args.log = False
    args.quiet = True

    print(f"Benchmark: Runnig blocking on all {len(benchmarks)} benchmarks:")
    start = time.time()
    

    reports = {}
    for benchmark in benchmarks:
        try:
            report = run_benchmark(benchmark, args)
        except NotImplementedError:
            continue
        
        reports[benchmark] = report["stats"]["block"]
        reports[benchmark]["similarity_cutoff"] = block_similarities[benchmark]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")
    
    df = report_to_dataframe(reports)
    file_name = save(df, name)
    
    # generate markdown table
    df = df[["benchmark", "similarity_cutoff", "percent_blocked", "f1", "throughput"]]
    field_names = {
        "benchmark": "Benchmark",
        "total_pairs": "Total Pairs",
        "similarity_cutoff": "Similarity Cutoff (0-100)",
        "percent_blocked": "Percent Blocked",
        "f1": "F1",
        "throughput": "Throughput (pps)",
    }
    df = df.rename(columns=field_names)
    
    tabulate(df, name)
    plot(file_name)
    show(df)

    return reports
