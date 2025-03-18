from libem.prepare.datasets import abt_buy
from benchmark.run import args
import numpy as np
from libem.cascade.function import online

def main():
    online(args(), abt_buy, num_pairs=100, threshold=0.9)
    

if __name__ == '__main__':
    main()