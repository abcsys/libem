import os
import random
from typing import Iterable

LIBEM_SAMPLE_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..', '..',
    'libem-sample-data')


def load(dataset: Iterable[dict], num_samples=-1, stringify=True) \
        -> ([str], [str], [int]):
    if num_samples > 0:
        dataset = random.sample(
            list(dataset),
            num_samples,
        )

    left, right, labels = [], [], []
    for data in dataset:
        left.append(str(data['left']) if stringify else data['left'])
        right.append(str(data['right']) if stringify else data['right'])
        labels.append(data.get('label', -1))
    return left, right, labels
