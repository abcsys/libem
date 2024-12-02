import numpy as np
from benchmark.run import args
import json
from libem.prepare.datasets import abt_buy, beer, itunes_amazon
from libem.cascade.function import online
from util import sensitivity_analysis, generate_stats, confidence_cost_plot, confidence_f1_plot, plot_result, save_results, compare_results

def bench():
    results_data = online(args(), dataset=abt_buy, num_pairs=None, threshold=0.9)
    compare_results(results_data)
    cascade_stats, prematch_single, match_single = generate_stats(results_data)
    save_results(cascade_stats, prematch_single, match_single)
    plot_result(cascade_stats, prematch_single, match_single)


def sensitivity_analysis():
    # Perform sensitivity analysis
    thresholds = np.arange(0.1, 1.0, 0.1)
    f1_scores, costs = sensitivity_analysis(args(), abt_buy, thresholds, num_pairs=100)
    F1_SCORE = f1_scores
    COSTS = costs
    confidence_cost_plot(thresholds, COSTS)
    confidence_f1_plot(thresholds, F1_SCORE)



if __name__ == '__main__':
    bench()