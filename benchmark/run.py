import json
import argparse

import benchmark.classic as classic
import libem

classic = {
    'abt-buy': classic.benchmark_abt_buy,
    'amazon-google': classic.benchmark_amazon_google,
    'beer': classic.benchmark_beer,
    'challenging': classic.benchmark_challenging,
    'dblp-acm': classic.benchmark_dblp_acm,
    'dblp-scholar': classic.benchmark_dblp_scholar,
    'fodors-zagats': classic.benchmark_fodors_zagats,
    'itunes-amazon': classic.benchmark_itunes_amazon,
    'walmart-amazon': classic.benchmark_walmart_amazon
}


def benchmark(args):
    # classic benchmarks
    name = args.name.lower().replace('_', '-')
    print(f"Benchmark: Matching {args.num_pairs if args.num_pairs > 0 else 'all'}"
          f" {'pair' if args.num_pairs == 1 else 'pairs'}"
          f" from the {name} benchmark.")
    benchmark_func = classic[name]
    benchmark_func(args)

    # ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("-n", "--name", dest='name', nargs='?',
                        help="The name of the benchmark.",
                        type=str, default='amazon-google')
    parser.add_argument("-p", "--num-pairs", dest='num_pairs', nargs='?',
                        help="Number of pairs to run through. Set as <= 0 to run through the entire dataset.",
                        type=int, default=5)
    parser.add_argument("-s", "--start", dest='start', nargs='?',
                        help="The index of the dataset to start from.",
                        type=int, default=0)
    parser.add_argument("-f", "--file", dest='file', nargs='?',
                        help="Name of the file to save to, will append '.json'.",
                        type=str, default='')
    parser.add_argument("-m", "--model", dest='model', nargs='?',
                        help="The OpenAI model to use.",
                        type=str, default='gpt-4o')
    parser.add_argument("--seed", dest='seed', nargs='?',
                        help="Random seed to use.",
                        type=int, default=libem.LIBEM_SEED)
    parser.add_argument("--no-shuffle", dest='shuffle',
                        help="Don't shuffle the dataset.",
                        action='store_false', default=True)
    parser.add_argument("--no-schema", dest='schema',
                        help="Turn off the dataset schema.",
                        action='store_false', default=True)
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
    parser.add_argument("-k", "--kwargs", dest='kwargs', type=json.loads,
                        help="Additional args that apply to specific benchmark files, in JSON format.")
    parser.add_argument("-v", "--verbose", dest='verbose', help="Print intermediate results for each pair to console.",
                        action='store_true', default=False)
    # todo: reuse arguments from cli/libem instead
    args = parser.parse_args()
    benchmark(args)
