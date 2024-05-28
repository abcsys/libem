import argparse
import benchmark
import libem
from libem.core.struct import Prompt
from libem.match.prompt import rule
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
    # if args.tune:
    #     learned_rules = libem.tune(train_set=train_set, test_set=test_set,
    #                             num_train_sample=250, num_test_sample=0,
    #                             learn_model='gpt-4-turbo', match_model='gpt-4-turbo',
    #                             num_iter=5)
    learned_rules = Prompt.Rule(rules=[
"1. If the products are from the same series (e.g., 'Adobe Creative Suite') but different versions or editions, do not match unless explicitly stated as compatible.",
"2. If the price difference exceeds 50%, do not match, unless the product titles and manufacturers are identical.",
"3. If one product title contains a specific year or edition number and the other does not, do not match.",
"4. If one title mentions a specific plaform (e.g., 'mac', 'win') and the other does not, do not match, regardless of title similarity.",
"5. If the product titles are identical but the manufacturers are different, do not match unless there is evidence of a rebranding or acquisition.",
"6. If the product titles suggest different functionalities (e.g., 'server software' vs. 'client software'), do not match.",
"7. If one title mentions a specific language or regional version (e.g., 'Japanese' vs. 'French'), do not match."
"8. 'upsale' and 'upgrade' are not the same.\n"
         ])
        
    # set model-specific config
    args.model = 'gpt-4-turbo'
    
    libem.calibrate({"libem.match.prompt.rule": learned_rules})

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
                        action='store_false', default=True)
    parser.add_argument("--verbose", dest='verbose', help="Print intermediate results for each pair to console.", 
                        action='store_true', default=False)
    parser.add_argument("--browse", dest='browse', help="Enable the browse tool.", 
                        action='store_true', default=False)
    parser.add_argument("--tune", dest='tune', help="Redo tuning.", 
                        action='store_true', default=False)
    
    args = parser.parse_args()
    main(args)