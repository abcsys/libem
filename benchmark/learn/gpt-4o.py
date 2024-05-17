import argparse
import benchmark
import libem
from libem.core.struct import Prompt
from libem.prepare.datasets import (
    abt_buy, amazon_google, dblp_acm,
    walmart_amazon, dblp_scholar
)

datasets = {
    'abt-buy': abt_buy,
    'amazon-google': amazon_google,
    'dblp-acm': dblp_acm,
    'walmart-amazon': walmart_amazon,
    'dblp-scholar': dblp_scholar
}

def main(args):
    dataset_name = args.dataset.lower().replace('_', '-')
    train_set = list(datasets[dataset_name].read_train(args.schema))
    test_set = list(datasets[dataset_name].read_test(args.schema))
    
    # tune
    if args.tune:
        learned_rules = libem.tune(train_set=train_set, test_set=test_set,
                                num_train_sample=250, num_test_sample=0,
                                learn_model='gpt-4o', match_model='gpt-4o',
                                num_iter=3)
        
    # set model-specific config
    args.model = 'gpt-4o'
    libem.calibrate({
        "libem.match.prompt.rule":
            Prompt(default=learned_rules)})

    benchmark.benchmark(args)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
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
                        action='store_true', default=True)
    parser.add_argument("--no_shuffle", dest='shuffle', help="Don't shuffle the dataset.", 
                        action='store_true', default=True)
    parser.add_argument("--verbose", dest='verbose', help="Print intermediate results for each pair to console.", 
                        action='store_true', default=False)
    parser.add_argument("--browse", dest='browse', help="Enable the browse tool.", 
                        action='store_true', default=False)
    parser.add_argument("--tune", dest='tune', help="Redo tuning.", 
                        action='store_true', default=False)
    
    args = parser.parse_args()
    main(args)