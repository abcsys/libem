import pprint
import time
import libem
import numpy as np
from libem.core.eval import precision, recall, f1

pp = pprint.PrettyPrinter(sort_dicts=False)

def main():
    ds_l = [
        {
            "name": "Microsoft Xbox series x - Game Console - 8K - HDR - 1 TB SSD",
            "manufacturer": "Microsoft",
            "price": "$499.99"
        },
        {
            "name": "Microsoft Xbox One S Console 1TB All-Digital Edition",
            "manufacturer": None,
            "price": "$ 159.99"
        },
        {
            "name": "Sony PlayStation 5 - Digital Edition",
            "manufacturer": "Sony",
            "price": "$499.99"
        }
    ]
    ds_r = [
        {
            "name": "Microsoft - Xbox Series X 1TB Console - Black",
            "rating": 4.92,
            "price": 499.99
        },
        {
            "name": "Microsoft Xbox Series S 512gb Game All-Digital Console, Renewed",
            "rating": 4.73,
            "price": 340.40
        },
        {
            "name": "Sony PlayStation 5 - Digital Edition",
            "rating": 4.51,
            "price": 479.99
        }
    ]
    matches = [
        {
            "left": {
                "name": "Microsoft Xbox series x - Game Console - 8K - HDR - 1 TB SSD",
                "manufacturer": "Microsoft",
                "price": "$499.99"
            },
            "right": {
                "name": "Microsoft - Xbox Series X 1TB Console - Black",
                "rating": 4.92,
                "price": 499.99
            }
        },
        {
            "left": {
                "name": "Sony PlayStation 5 - Digital Edition",
                "manufacturer": "Sony",
                "price": "$499.99"
            },
            "right": {
                "name": "Sony PlayStation 5 - Digital Edition",
                "rating": 4.51,
                "price": 479.99
            }
        }
    ]
    
    print("Left dataset:")
    pp.pprint(ds_l)
    print("\nRight dataset:")
    pp.pprint(ds_r)
    
    potential_pairs = len(ds_l) * len(ds_r)
    print("\nNumber of potential matching pairs:", potential_pairs)
    print("Number of actual matching pairs:", len(matches))
    
    print("\nStarting blocking...")
    start_time = time.time()
    output = list(libem.block(ds_l, ds_r))
    block_time = time.time() - start_time
    print("Blocking done.")
    print("Number of pairs after blocking:", len(output))
    
    print("\nStarting matching...")
    predictions, actual = [], []
    start_time = time.time()
    for p in output:
        res = libem.match(p['left'], p['right'])['answer']
        if res == 'yes':
            predictions.append(1)
        else:
            predictions.append(0)
        if p in matches:
            actual.append(1)
        else:
            actual.append(0)
    match_time = time.time() - start_time
    print("Matching done.")
    print("Number of predicted matching pairs:", np.count_nonzero(predictions))
    
    print(f"\nF1 score\t\t{round(f1(actual, predictions) * 100, 2)}")
    print(f"Total time taken\t{round(block_time + match_time, 2)}s")
    time_needed = match_time / len(output) * potential_pairs
    time_saved = time_needed - block_time - match_time
    print(f"Time saved by blocking"
          f"\t{round(time_saved, 2)}s "
          f"({round(time_saved / time_needed * 100)}%)")

if __name__ == "__main__":
    main()