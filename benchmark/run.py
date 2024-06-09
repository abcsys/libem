import json
import argparse

import libem

from benchmark.classic import (
    abt_buy,
    amazon_google,
    beer,
    dblp_acm,
    dblp_scholar,
    fodors_zagats,
    itunes_amazon,
    walmart_amazon,
    challenging,
)

classic_benchmarks = {
    'abt-buy': abt_buy.run,
    'amazon-google': amazon_google.run,
    'beer': beer.run,
    'dblp-acm': dblp_acm.run,
    'dblp-scholar': dblp_scholar.run,
    'fodors-zagats': fodors_zagats.run,
    'itunes-amazon': itunes_amazon.run,
    'walmart-amazon': walmart_amazon.run,
    'challenging': challenging.run,
}


def run(args):
    # classic benchmarks
    name = args.name.lower().replace('_', '-')
    print(f"Benchmark: Matching {args.num_pairs if args.num_pairs > 0 else 'all'}"
          f" {'pair' if args.num_pairs == 1 else 'pairs'}"
          f" from the {name} benchmark.")
    benchmark_func = classic_benchmarks[name]
    benchmark_func(args)

    # ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark")

    # benchmark configurations
    parser.add_argument("-n", "--name", dest='name', nargs='?',
                        help="The name of the benchmark.",
                        type=str, default='amazon-google')
    parser.add_argument("-p", "--num-pairs", dest='num_pairs', nargs='?',
                        help="Number of pairs to run through. "
                             "Set as <= 0 to run through the entire dataset.",
                        type=int, default=5)
    parser.add_argument("-i", "--index", dest='start_index', nargs='?',
                        help="The index of the dataset to start from.",
                        type=int, default=0)
    parser.add_argument("-f", "--file", dest='file', nargs='?',
                        help="Name of the file to save to, will append '.json'.",
                        type=str, default='')
    parser.add_argument("--train", dest='train',
                        help="Use the training set.",
                        action='store_true', default=True)
    parser.add_argument("--no-shuffle", dest='shuffle',
                        help="Don't shuffle the dataset.",
                        action='store_false', default=True)
    parser.add_argument("--no-schema", dest='schema',
                        help="Turn off the dataset schema.",
                        action='store_false', default=True)
    parser.add_argument("--seed", dest='seed', nargs='?',
                        help="Random seed to use.",
                        type=int, default=libem.LIBEM_SEED)
    parser.add_argument("-q", "--quiet", dest='quiet',
                        help="Suppress messages for matching each pair.",
                        action='store_true', default=False)
    parser.add_argument("-k", "--kwargs", dest='kwargs', type=json.loads,
                        help="Additional args that apply to specific benchmark files, in JSON format.")

    # libem configurations
    parser.add_argument("-m", "--model", dest='model', nargs='?',
                        help="The OpenAI model to use.",
                        type=str, default='gpt-4o')
    parser.add_argument("--browse", dest='browse',
                        help="Enable the browse tool.",
                        action='store_true', default=False)
    parser.add_argument("--cot", dest='cot',
                        help="Enable chain of thought.",
                        action='store_true', default=False)
    parser.add_argument("--confidence", dest='confidence',
                        help="Report confidence score.",
                        action='store_true', default=False)
    parser.add_argument("-d", "--debug", dest='debug',
                        help="Enable debug mode.",
                        action='store_true', default=False)
    parser.add_argument("-g", "--guess", dest='guess',
                        help="Match by guessing.",
                        action='store_true', default=False)

    args = parser.parse_args()
    run(args)
