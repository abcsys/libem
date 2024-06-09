"""Plot the benchmark results."""

import json
import numpy as np
import argparse

import matplotlib.pyplot as plt


def plot(args):
    """Plot the benchmark results."""
    # load the results
    results = []
    for result_file in args.results:
        with open(result_file, 'r') as f:
            results.extend(json.load(f))

    # get the x-axis labels
    x_labels = []
    for result in results:
        x_labels.append(result['name'])

    # get the y-axis values
    y_values = {}
    for result in results:
        for key, value in result['results'].items():
            if key not in y_values:
                y_values[key] = []
            y_values[key].append(value)

    # plot the results
    fig, ax = plt.subplots()
    x = np.arange(len(x_labels))
    width = 0.35
    for i, (key, values) in enumerate(y_values.items()):
        ax.bar(x + i * width, values, width, label=key)

    ax.set_ylabel('Time (s)')
    ax.set_title('Benchmark Results')
    ax.set_xticks(x + width * (len(y_values) - 1) / 2)
    ax.set_xticklabels(x_labels)
    ax.legend()

    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Plot the benchmark results.')
    parser.add_argument('results', nargs='+', help='The JSON files containing the benchmark results.')
    args = parser.parse_args()

    plot(args)
