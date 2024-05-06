import libem
import argparse
import numpy as np
import json
import os
from datetime import datetime
from libem.prepare.datasets import abt_buy, amazon_google, dblp_acm, walmart_amazon, dblp_scholar
from libem.core.eval import f1

datasets = {
    'abt-buy': abt_buy,
    'amazon-google': amazon_google,
    'dblp-acm': dblp_acm,
    'walmart-amazon': walmart_amazon,
    'dblp-scholar': dblp_scholar
}

def main(args):
 
    if args.verbose:
        print(f"Matching {args.num_pair} from Amazon Google product dataset.")
    
    truth, predictions, result = [], [], []
    dataset = args.dataset.lower().replace('_', '-')
        
    for i, data in enumerate(datasets[dataset].read_test(args.schema)):
        
        e1 = data['left']
        e2 = data['right']
        label = data['label']

        is_match = libem.match(e1, e2)
        
        if 'yes' in is_match.lower():
            predictions.append(1)
        else:
            predictions.append(0)
        truth.append(label)
        
        result.append({
            'Entity 1': e1,
            'Entity 2': e2,
            'Match': is_match,
            'Label': label
        })
        
        if args.verbose:
            print("\nPair: ", i+1)
            print(f"Entity 1: {e1}\nEntity 2: {e2}\nMatch: {is_match}; Label: {label}\n")
            
        if args.num_pair > 0 and i+1 >= args.num_pair:
            break
    
    # save results
    out_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], 
                                          f'results/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.json')
    with open(out_file, 'w') as f:
        json.dump(result, f, indent=4)
    
    print("Done.")
    print("F1 score:", round(f1(np.array(truth), np.array(predictions)) * 100, 2))
    print("Results saved to:", out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("--dataset", dest='dataset', nargs='?', help="The dataset to benchmark.", type=str, default='amazon-google')
    parser.add_argument("--schema", dest='schema', nargs='?', help="The dataset to benchmark.", type=bool, default=True)
    parser.add_argument("--num_pair", dest='num_pair', nargs='?', help="Number of pairs to run through. Set as 0 to run through the entire dataset.", type=int, default=5)
    parser.add_argument("--verbose", dest='verbose', nargs='?', help="If true, will print out the result for each pair.", type=bool, default=False)
    args = parser.parse_args()
    main(args)
