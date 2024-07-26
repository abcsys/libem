import json
import argparse

import libem

import benchmark
import benchmark.util as util


def run(args) -> dict:
    if args.input_file:
        args.name = args.input_file.split('/')[-1].split(".")[0]
        benchmark_func = run_from_file
    else:
        args.name = args.name.lower().replace('_', '-')
        benchmark_func = benchmark.benchmarks[args.name]

    return benchmark_func(args)


def run_from_file(args) -> dict:
    """
    Entity pairs should follow the Libem result format:
    [{
        "left": {...},
        "right": {...},
        "label": 0,
      }, ...]
    These pairs could be nested under a "results.match",
    "fp", "fn", "tn", "tp" keys or directly in the JSON file.
    """
    pairs = []
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    if isinstance(input_data, list):
        pairs = input_data
    else:
        if "results" in input_data:
            pairs = input_data["results"].get("match", pairs)
        if "fp" in input_data:
            pairs.extend(input_data["fp"])
        if "fn" in input_data:
            pairs.extend(input_data["fn"])
        if "tp" in input_data:
            pairs.extend(input_data["tp"])
        if "tn" in input_data:
            pairs.extend(input_data["tn"])
        if len(pairs) == 0:
            raise ValueError(f"No entity pairs found in input file, "
                             f"check the input format {run_from_file.__doc__}.")

    # ... other processing steps
    return util.benchmark(pairs, args)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("benchmark")

    # intput configurations
    parser.add_argument("-n", "--name", dest='name', nargs='?',
                        help="The name of the benchmark.",
                        type=str, default='abt-buy')
    parser.add_argument("-i", "--input-file", dest='input_file', nargs='?',
                        help="Name of the input file to use as a dataset.",
                        type=str, default='')
    parser.add_argument("-o", "--output-file", dest='output_file', nargs='?',
                        help="Name of the file to save to, will append '.json'.",
                        type=str, default='')
    parser.add_argument("-p", "--num-pairs", dest='num_pairs', nargs='?',
                        help="Number of pairs to run through. "
                             "Set as <= 0 to run through the entire dataset.",
                        type=int, default=5)

    # dataset configurations
    parser.add_argument("--start-index", dest='start_index', nargs='?',
                        help="The index of the dataset to start from.",
                        type=int, default=0)
    parser.add_argument("--no-shuffle", dest='shuffle',
                        help="Don't shuffle the dataset.",
                        action='store_false', default=True)
    parser.add_argument("--no-schema", dest='schema',
                        help="Turn off the dataset schema.",
                        action='store_false', default=True)

    # benchmark configurations
    parser.add_argument("--block", dest='block',
                        help="Perform blocking.",
                        action='store_true', default=False)
    parser.add_argument("--no-match", dest='match',
                        help="Skip the matching phase.",
                        action='store_false', default=True)
    parser.add_argument("--seed", dest='seed', nargs='?',
                        help="Random seed to use.",
                        type=int, default=libem.LIBEM_SEED)
    parser.add_argument("-q", "--quiet", dest='quiet',
                        help="Suppress messages.",
                        action='store_true', default=False)
    parser.add_argument("-k", "--kwargs", dest='kwargs', type=json.loads,
                        help="Additional args that apply to specific "
                             "benchmark files, in JSON format.")
    parser.add_argument("--no-log", dest='log',
                        help="Don't log the results.",
                        action='store_false', default=True)
    parser.add_argument("--icl", dest='icl', nargs='?',
                        help="The strategy to use for in-context learning.",
                        type=str, default="similar-shots")
    parser.add_argument("--num-shots", dest='num_shots', nargs='?',
                        help="The number of shots to use for in-context learning.",
                        type=int, default=0)

    # libem configurations
    parser.add_argument("-m", "--model", dest='model', nargs='?',
                        help="The OpenAI model to use.",
                        type=str, default=libem.parameter.model())
    parser.add_argument("--temperature", dest='temperature', nargs='?',
                        help="The temperature to use for model call.",
                        type=float, default=libem.parameter.temperature())
    parser.add_argument("--batch-size", dest='batch_size', nargs='?',
                        help="The batch size to use for matching.",
                        type=int, default=1)
    parser.add_argument("--browse", dest='browse',
                        help="Enable the browse tool.",
                        action='store_true', default=False)
    parser.add_argument("--cot", dest='cot',
                        help="Enable chain of thought.",
                        action='store_true', default=False)
    parser.add_argument("--confidence", dest='confidence',
                        help="Report confidence score.",
                        action='store_true', default=False)
    parser.add_argument("--similarity", dest='similarity', nargs='?',
                        help="The similarity score cutoff for block, between 0-100.",
                        type=int, default=-1)
    parser.add_argument("-r", "--rules", dest='rules', nargs='*',
                        help="List of rules to add to match.",
                        type=str, default='')

    parser.add_argument("--sync", dest='sync',
                        help="Run Libem in synchronous mode.",
                        action='store_true', default=False)
    parser.add_argument("-d", "--debug", dest='debug',
                        help="Enable debug mode.",
                        action='store_true', default=False)
    parser.add_argument("-g", "--guess", dest='guess',
                        help="Match by guessing.",
                        action='store_true', default=False)

    return parser.parse_args()


def main():
    run(args())


if __name__ == "__main__":
    main()
