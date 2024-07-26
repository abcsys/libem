import pprint

from libem.optimize import profile
from libem.prepare.datasets import abt_buy as dataset

if __name__ == "__main__":
    pprint.pprint(
        profile(dataset.read_train(), num_samples=10),
        sort_dicts=False,
    )
