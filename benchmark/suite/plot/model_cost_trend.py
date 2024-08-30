import os
import seaborn as sns

from datetime import datetime
from matplotlib import pyplot as plt, ticker

import benchmark as bm
from benchmark.suite.plot.util import load


def plot(args):
    '''
    kwargs:
        models (list[str]): models to include in the plot.
        benchmarks (list[str]): benchmarks to include in the plot.
    '''
    results = load(args)
    
    # calculate pairs per $
    def ppd(x):
        x['num_pairs'] = x['tp'] + x['fp'] + x['tn'] + x['fn']
        if x['cost'] > 0:
            x['ppd'] = x['num_pairs'] / x['cost']
        else:
            x['ppd'] = -1
        return x
    results = results.apply(ppd, axis=1)
    
    # order by ppd
    results = results[results['ppd'] >= 0]
    results = results.groupby('model')[['ppd']].mean().sort_values('ppd')['ppd'].reset_index()
    # dummy column needed for markers
    results['label'] = 1
    
    # calculate range and positioning numbers
    y_range = results['ppd'].max() - results['ppd'].min()
    y_unit = y_range / 25
    x_unit = len(results) / 110
    
    # plot
    sns.set_theme(font_scale=1.4)
    fig, ax = plt.subplots()
    fig.set_size_inches(9, 5)
    
    # draw AWS baseline
    plt.axhline(4000, color='#3498db', linewidth=2, linestyle='--')
    ax.text(len(results) - 1.7, 4000 + y_unit, "AWS ER", color='#3498db', size=14)
    
    # plot line graph with value labels
    sns.lineplot(results, x='model', y='ppd', color='#2ecc71', style='label', markers=True, 
                 ax=ax, linewidth=3, legend=False, markersize=8)
    for item in results.iterrows():
        text = f"{format(int(item[1]['ppd']), ',')}"
        x_space = len(text) * x_unit
        ax.text(item[0] - x_space, item[1]['ppd'] + y_unit, text, color='#000', size=15)

    plt.xticks(rotation=90)
    plt.locator_params(axis='y', nbins=5)
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.ylim(-y_unit, y_range + y_unit * 3)
    plt.title('')
    plt.xlabel('')
    plt.ylabel("Pairs per Dollar")
    
    output_file = os.path.join(
                    bm.figure_dir,
                    f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
                    "model-cost-trend.svg")
    plt.savefig(output_file, format='svg', bbox_inches = "tight")
    print(f"Model cost trend plot saved to: {output_file}")
