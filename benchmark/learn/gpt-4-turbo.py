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
    # if args.tune:
    #     learned_rules = libem.tune(train_set=train_set, test_set=test_set,
    #                             num_train_sample=100, num_test_sample=0,
    #                             learn_model='gpt-4-turbo', match_model='gpt-4-turbo',
    #                             num_iter=3)
    learned_rules = Prompt.Rule(rules=[
        "1. If the manufacturer names are different or one is missing, and the product titles do not match exactly, classify as 'no'.",
        "2. If one product title contains a specific model or version number but the other does not, classify as 'no'.",
        "3. If the product titles contain the same unique product name and version number, classify as 'yes'.",
        "4. If the product titles are similar but refer to different versions or editions (e.g., 'deluxe' vs. 'standard'), classify as 'no'.",
        "5. If the product titles are similar but one includes additional descriptors that suggest a different product scope or bundle (e.g., 'upgrade', 'bundle', 'suite'), classify as 'no'.",
        "6. If the prices are vastly different, classify as 'no', unless both the titles and manufacturers match exactly.",
        "7. If one title includes specifies a quantity (e.g. 3pk) but the other does not, classify as 'no'.",
        "8. If the products are from the same manufacturer and the titles suggest they are different editions or releases of the same product line, classify as 'no'.",
        "9. If the product titles contain the same base name but different extensions (e.g., 'Pro' vs. 'Pro Upgrade'), classify as 'no'.",
        "10. If both titles include terms that typically indicate the same type of product but are formatted differently (e.g., abbreviations vs. full names), classify as 'no' unless other information (like exact matching part numbers) suggests they are the same product.",
        ])
        
    # set model-specific config
    args.model = 'gpt-4-turbo'
    libem.calibrate({
        "libem.match.prompt.rule":
            Prompt(default=learned_rules)})

    benchmark.benchmark(args, learned_rules)
    


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