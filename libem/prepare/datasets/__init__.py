import os
import json
import random
from typing import Iterable

LIBEM_SAMPLE_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..', '..',
    'libem-sample-data')

from libem.prepare.datasets.clustering import (
    febrl,
    amazon_google,
    dblp_scholar,
    itunes_amazon,
)

datasets = {
    'febrl': febrl.load_raw,
    'amazon-google': amazon_google.load_raw,
    'dblp-scholar': dblp_scholar.load_raw,
    'itunes-amazon': itunes_amazon.load_raw,
}


def load(dataset: Iterable[dict], num_samples=-1, stringify=True) \
        -> ([str], [str], [int]):
    if num_samples > 0:
        dataset = random.sample(
            list(dataset),
            num_samples,
        )

    left, right, labels = [], [], []
    for data in dataset:
        left.append(json.dumps(data['left']) if stringify else data['left'])
        right.append(json.dumps(data['right']) if stringify else data['right'])
        labels.append(data.get('label', -1))
    return left, right, labels
