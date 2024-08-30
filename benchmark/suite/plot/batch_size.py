import os
import numpy as np
import pandas as pd
import seaborn as sns

from datetime import datetime
from matplotlib import pyplot as plt, ticker

import benchmark as bm
from benchmark.suite.plot.util import load


def plot(args):
    '''
    kwargs:
        benchmark (str): benchmark to plot, 
                         empty to plot the last batch suite result.
    '''
    # get the newest batch suite result
    result_file = None
    for file in os.scandir(bm.result_dir):
        # extract suite and benchmark name from result file name
        suite, name = file.name[20:31], file.name[32:-4]
        if suite == 'suite-batch':
            if args.kwargs and 'benchmark' in args.kwargs:
                if name == args.kwargs['benchmark']:
                    result_file = file
            else:
                result_file = file
    
    if not result_file:
        raise ValueError("No batch suite results found.")
    results = pd.read_csv(result_file)
    
    # calculate difference from baseline
    baseline = results[results['batch_size'] == 1].iloc[0]
    
    def delta(x):
        x['throughput'] = x['throughput'] - baseline['throughput']
        x['cost'] = baseline['cost'] - x['cost']
        return x
    
    results = results.apply(delta, axis=1)
    
    # plot
    sns.set_theme(font_scale=1.4)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(12, 5)
    sns.barplot(results, x='batch_size', y='throughput', color="#2ecc71", ax=ax1, width=0.8)
    ax1.axhline(0, color='#e74c3c')
    ax1.set(xlabel="Batch Size vs Throughput", ylabel="Throughput (pps)", title="")
    ax1.get_xaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, p: int(x)))
    sns.barplot(results, x='batch_size', y='cost', color="#2ecc71", ax=ax2, width=0.8)
    ax2.set(xlabel="Batch Size vs Cost Savings", ylabel="Cost Savings ($)", title="")
    ax2.get_xaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, p: int(x)))
    plt.tight_layout()
    
    output_file = os.path.join(
                    bm.figure_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    "batch-size.svg")
    plt.savefig(output_file, format='svg', bbox_inches = "tight")
    print(f"Batch size plot saved to: {output_file}")
