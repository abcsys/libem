import pprint

from libem.optimize import profile
from libem.prepare.datasets.abt_buy import read_train

if __name__ == "__main__":
    num_samples = 10

    dataset = []
    for i, sample in enumerate(read_train()):
        dataset.append(sample)
        if i == num_samples - 1:
            break

    pprint.pprint(
        profile(dataset),
        sort_dicts=False,
    )
