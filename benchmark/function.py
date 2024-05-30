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
from libem.core.struct import Prompt
from libem.prepare.datasets import (
    abt_buy, amazon_google, beer, dblp_acm,
    dblp_scholar, fodors_zagats, itunes_amazon, walmart_amazon
)
from libem.core.eval import confusion_matrix, precision, recall, f1

random.seed(libem.LIBEM_SEED)
datasets = {
    'abt-buy': abt_buy,
    'amazon-google': amazon_google,
    'beer': beer,
    'dblp-acm': dblp_acm,
    'dblp-scholar': dblp_scholar,
    'fodors-zagats': fodors_zagats,
    'itunes-amazon': itunes_amazon,
    'walmart-amazon': walmart_amazon
}


def benchmark(args):
    total_start_time = time.time()
    
    if not args.verbose:
        libem.LIBEM_LOG_LEVEL = logging.WARNING
    
    # set configs
    libem.calibrate({
        "libem.match.parameter.tools": ["libem.browse"] if args.browse else [],  # turn off sub-tools
        "libem.match.parameter.model": args.model,
    })
    
    truth, predictions, result = [], [], []
    dataset_name = args.dataset.lower().replace('_', '-')
    dataset = list(datasets[dataset_name].read_test(args.schema))
    if args.shuffle:
        random.shuffle(dataset)
    
    # telemetry
    total_input_tokens, total_output_tokens = 0, 0
    
    print(f"Benchmark: Matching {args.num_pair if args.num_pair > 0 else 'all'}"
          f" {'pair' if args.num_pair == 1 else 'pairs'}"
          f" from the {dataset_name} dataset.")

    for i, data in enumerate(dataset[args.start:]):
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
            is_match = None
            start_time = time.time()
            
            while is_match is None:
                # retry if model times out
                num_timeouts = 0
                try:
                    is_match = libem.match(e1, e2)
                except libem.ModelTimedoutException:
                    num_timeouts += 1
            if num_timeouts > 0:
                print(f"Model timed out {num_timeouts} time(s).")
            
            # get unparsed model output and telemetry
            latency = time.time() - start_time
            pred = [i['match']['model_output'] for i in t.get() if 'match' in i][0]
            input_tokens = sum([i['model']['num_input_tokens'] for i in t.get() if 'model' in i])
            output_tokens = sum([i['model']['num_output_tokens'] for i in t.get() if 'model' in i])
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            
            # append results
            result.append({
                'entity_1': e1,
                'entity_2': e2,
                'pred': is_match,
                'label': label,
                'model_output': pred,
                'tools_used': [i['tool'] for i in t.get() if 'tool' in i],
                'latency': round(latency, 2),
                'tokens': {'input_tokens': input_tokens, 'output_tokens': output_tokens}
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
    
    # get stats
    metrics = [precision, recall, f1]
    conf_mat = confusion_matrix(np.array(truth), np.array(predictions))
    stats = {m.__name__: round(m(np.array(truth), np.array(predictions)) * 100, 2) for m in metrics}
    stats['latency'] = round(time.time() - total_start_time, 2)
    stats['tokens'] = {
        'input_tokens': total_input_tokens,
        'output_tokens': total_output_tokens
    }
    stats['confusion_matrix'] = {
        'tp': int(conf_mat[0]),
        'tn': int(conf_mat[2]),
        'fp': int(conf_mat[1]),
        'fn': int(conf_mat[3])
    }
    

    with open(out_file, 'w') as f:
        json.dump({
                'stats': stats,
                'results': result
            }, f, indent=4)

    print(f"Benchmark: Done in {stats['latency']}.")
    print("Benchmark: Precision\t", stats['precision'])
    print("Benchmark: Recall\t", stats['recall'])
    print("Benchmark: F1 score\t", stats['f1'])
    print("Benchmark: Results saved to:", out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("--model", dest='model', nargs='?', help="The OpenAI model to use.", 
                        type=str, default='gpt-4-turbo')
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
    
    args = parser.parse_args()
    benchmark(args)
