import os
import copy
import time

import libem
import benchmark.run
from benchmark.classic import dataset_benchmarks
from benchmark.suite.util import (report_to_dataframe, 
                                  tabulate, plot, 
                                  save, show)

name = os.path.basename(__file__).replace(".py", "")


def run(args):
    '''
    kwargs:
        dataset (str): the dataset to perform batch size benchmark.
                       Defaults to 'abt-buy'.
    '''
    
    args.block = False
    args.match = True
    args.num_pairs = -1
    if args.kwargs and 'dataset' in args.kwargs:
        dataset = args.kwargs['dataset']
    else:
        dataset = 'abt-buy'
    
    # do not use downstream log/print
    log = args.log
    args.log = False
    quiet = args.quiet
    args.quiet = True
    
    batch_sizes = [1, 4, 16, 64, 128, 256, 512]
    
    print(f"Benchmark: Varying the batch size on the {dataset} datasets:")
    start = time.time()
    
    reports = {}
    for batch_size in batch_sizes:
        args.batch_size = batch_size
        args.name = dataset
        
        # create a deep copy of args to pass into benchmark
        args_cpy = copy.deepcopy(args)

        libem.reset()
        report = dataset_benchmarks[dataset](args)
        reports[batch_size] = report["stats"]["match"]

    print(f"Benchmark: Suite done in: {time.time() - start:.2f}s.")
    
    df = report_to_dataframe(reports, key_col="batch_size")
    if log:
        save(df, f"{name}-{dataset}")

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
    
    if log:
        tabulate(df, f"{name}-{dataset}")
    
    if not quiet:
        plot(df)
        show(df)

    return reports
