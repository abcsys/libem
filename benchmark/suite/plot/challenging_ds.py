import os
import copy
import seaborn as sns

from datetime import datetime
from matplotlib import pyplot as plt

import benchmark as bm
from benchmark.suite.plot.util import load


def plot(args):
    '''
    kwargs:
        models (list[str]): models to include in the plot.
    '''
    
    # create a deep copy of args before making changes
    args = copy.deepcopy(args)
    
    if not args.kwargs:
        args.kwargs = {}
    args.kwargs['benchmarks'] = ['classic.challenging']
    results = load(args)
    
    # order by f1 score
    order = results.sort_values('f1')['model']
    
    # plot
    plt.figure(figsize=(7, 5))
    sns.set_theme(font_scale=1.4)
    sns.barplot(results, x='model', y='f1', color='#2ecc71', order=order)
    plt.xticks(rotation=90)
    plt.ylim(0, 40)
    plt.yticks([0, 10, 20, 30, 40])
    plt.title("")
    plt.xlabel('')
    plt.ylabel("F1 Score (%)")
    
    output_file = os.path.join(
                    bm.figure_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    "challenging-ds-f1.svg")
    plt.savefig(output_file, format='svg', bbox_inches = "tight")
    print(f"Model F1 plot saved to: {output_file}")
