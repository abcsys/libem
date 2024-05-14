import argparse
import json
import logging
import numpy as np
import time
import random
import os
from pathlib import Path
from datetime import datetime

import libem
from libem.prepare.datasets import (
    abt_buy, amazon_google, dblp_acm,
    walmart_amazon, dblp_scholar
)
from libem.core.eval import precision, recall, f1

random.seed(libem.parameter.seed())
datasets = {
    'abt-buy': abt_buy,
    'amazon-google': amazon_google,
    'dblp-acm': dblp_acm,
    'walmart-amazon': walmart_amazon,
    'dblp-scholar': dblp_scholar
}


def main(args):
    if not args.verbose:
        libem.LIBEM_LOG_LEVEL = logging.WARNING
    
    truth, predictions, result = [], [], []
    dataset_name = args.dataset.lower().replace('_', '-')
    dataset = list(datasets[dataset_name].read_test(args.schema))
    if args.shuffle:
        random.shuffle(dataset)
    
    start_time = time.time()
    
    print(f"Benchmark: Matching {args.num_pair if args.num_pair > 0 else 'all'}"
          f" {'pair' if args.num_pair == 1 else 'pairs'}"
          f" from the {dataset_name} dataset.")

    for i, data in enumerate(dataset):
        if i < args.start:
            continue

        e1 = data['left']
        e2 = data['right']
        label = data['label']
        
        if args.verbose:
            print("\nPair: ", i + 1)
            print(f"Entity 1: {e1}\nEntity 2: {e2}")

        # call match
        with libem.trace as t:
            is_match = libem.match(e1, e2)
            
            # get unparsed model output
            pred = [i['match']['model_output'] for i in t.get() if 'match' in i][0]
            
            # cache results
            result.append({
                'entity_1': e1,
                'entity_2': e2,
                'tools_used': [i['tool'] for i in t.get() if 'tool' in i],
                'model_output': pred,
                'pred': is_match,
                'label': label
            })

        # track results for evaluation metrics
        if is_match == 'yes':
            predictions.append(1)
        else:
            predictions.append(0)
        truth.append(label)

        if args.verbose:
            print(pred)
            print(f"Match: {is_match}; Label: {label}\n")

        # check num_pair stop condition
        if args.num_pair > 0 and i + 1 >= args.num_pair:
            break

    # save results to ./results
    results_folder = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'results')
    Path(results_folder).mkdir(parents=True, exist_ok=True)
    if len(args.file) > 0:
        out_file = os.path.join(results_folder, f'{args.file}.json')
    else:
        out_file = os.path.join(results_folder, f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.json')

    with open(out_file, 'w') as f:
        json.dump(result, f, indent=4)

    print(f"Benchmark: Done in {time.time() - start_time}.")
    print("Benchmark: Precision\t", round(precision(np.array(truth), np.array(predictions)) * 100, 2))
    print("Benchmark: Recall\t", round(recall(np.array(truth), np.array(predictions)) * 100, 2))
    print("Benchmark: F1 score\t", round(f1(np.array(truth), np.array(predictions)) * 100, 2))
    print("Benchmark: Results saved to:", out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("--dataset", dest='dataset', nargs='?', help="The dataset to benchmark.", type=str,
                        default='amazon-google')
    parser.add_argument("--num_pair", dest='num_pair', nargs='?',
                        help="Number of pairs to run through. Set as 0 to run through the entire dataset.", type=int,
                        default=5)
    parser.add_argument("--start", dest='start', nargs='?', help="The index of the dataset to start from.", type=int, 
                        default=0)
    parser.add_argument("--file", dest='file', nargs='?', help="Name of the file to save to, will append '.json'.", 
                        type=str, default='')
    parser.add_argument("--no_schema", dest='schema', help="Turn off the dataset schema.",
                        action='store_true', default=True)
    parser.add_argument("--no_shuffle", dest='shuffle', help="Don't shuffle the dataset.", action='store_true', 
                        default=True)
    parser.add_argument("--verbose", dest='verbose', help="Print intermediate results for each pair to console.", 
                        action='store_true', default=False)
    
    args = parser.parse_args()
    main(args)
