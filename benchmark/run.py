import json
import argparse

import benchmark.datasets as datasets

dataset_map = {
    'abt-buy': datasets.benchmark_abt_buy,
    'amazon-google': datasets.benchmark_amazon_google,
    'beer': datasets.benchmark_beer,
    'dblp-acm': datasets.benchmark_dblp_acm,
    'dblp-scholar': datasets.benchmark_dblp_scholar,
    'fodors-zagats': datasets.benchmark_fodors_zagats,
    'itunes-amazon': datasets.benchmark_itunes_amazon,
    'walmart-amazon': datasets.benchmark_walmart_amazon
}


def run(args):
    name = args.dataset.lower().replace('_', '-')
    print(f"Benchmark: Matching {args.num_pair if args.num_pair > 0 else 'all'}"
          f" {'pair' if args.num_pair == 1 else 'pairs'}"
          f" from the {name} dataset.")
    benchmark_func = dataset_map[name]
    benchmark_func(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("--model", dest='model', nargs='?', help="The OpenAI model to use.",
                        type=str, default='gpt-4o')
    parser.add_argument("--dataset", dest='dataset', nargs='?', help="The dataset to benchmark.",
                        type=str, default='amazon-google')
    parser.add_argument("--num_pair", dest='num_pair', nargs='?',
                        help="Number of pairs to run through. Set as 0 to run through the entire dataset.",
                        type=int, default=5)
    parser.add_argument("--start", dest='start', nargs='?', help="The index of the dataset to start from.",
                        type=int, default=0)
    parser.add_argument("--file", dest='file', nargs='?', help="Name of the file to save to, will append '.json'.",
                        type=str, default='')
    parser.add_argument("--no_schema", dest='schema', help="Turn off the dataset schema.",
                        action='store_false', default=True)
    parser.add_argument("--no_shuffle", dest='shuffle', help="Don't shuffle the dataset.",
                        action='store_false', default=True)
    parser.add_argument("--verbose", dest='verbose', help="Print intermediate results for each pair to console.",
                        action='store_true', default=False)
    parser.add_argument("--browse", dest='browse', help="Enable the browse tool.",
                        action='store_true', default=False)
    parser.add_argument('--kwargs', dest='kwargs', type=json.loads,
                        help="Additional args that apply to specific benchmark files, in JSON format.")

    args = parser.parse_args()
    run(args)
