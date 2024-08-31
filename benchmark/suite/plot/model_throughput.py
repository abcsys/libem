import os
import numpy as np
import pandas as pd
import seaborn as sns

from datetime import datetime
from matplotlib import pyplot as plt

import benchmark as bm
from benchmark.suite.plot.util import load


def plot(args):
    '''
    kwargs:
        models (list[str]): models to include in the plot.
        benchmarks (list[str]): benchmarks to include in the plot.
    '''
    results = load(args)
    
    # order by f1 score
    order = results.groupby('model')[['throughput']].mean().sort_values('throughput').index
    
    # plot
    plt.figure(figsize=(9, 5))
    sns.set_theme(font_scale=1.4)
    sns.barplot(results, x='model', y='throughput', estimator=np.mean, capsize=.2, color='#2ecc71', order=order, width=0.7)
    plt.xticks(rotation=90)
    plt.title('')
    plt.xlabel('')
    plt.ylabel("Throughput (pps)")
    
    output_file = os.path.join(
                    bm.figure_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    "model-throughput.svg")
    plt.savefig(output_file, format='svg', bbox_inches = "tight")
    print(f"Model throughput plot saved to: {output_file}")
