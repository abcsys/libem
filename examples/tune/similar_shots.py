import random
import numpy as np
import fuzzywuzzy as fuzz
import pprint as pp

import libem
from libem.tune.learn.strategy import similar_shots
from libem.prepare.datasets import amazon_google as dataset
from libem.core.eval import report


def run():
    random.seed(1)
    num_tests = 10
    num_shots = 3

    test_set = random.sample(
        list(dataset.read_test()),
        num_tests
    )
    train_set = list(
        dataset.read_train()
    )

    libem.calibrate({"libem.match.parameter.model": "gpt-3.5-turbo"})

    print("Before few-shot:")

    truths, predictions = [], []
    for pair in test_set:
        with libem.trace as t:
            left, right = pair["left"], pair["right"]
            label = pair["label"]

            is_match = libem.match(left, right)

            pred = 1 if is_match["answer"] == "yes" else 0
            truths.append(label)
            predictions.append(pred)

    pp.pprint(
        report(truths, predictions),
        sort_dicts=False,
    )

    print("After few-shot:")

    truths, predictions = [], []
    for pair in test_set:
        shots = similar_shots.run(
            train_set, pair, num_shots,
        )
        with libem.trace as t:
            left, right = pair["left"], pair["right"]
            label = pair["label"]

            libem.calibrate({
                "libem.match.prompt.shots": shots,
            })

            is_match = libem.match(left, right)

            pred = 1 if is_match["answer"] == "yes" else 0
            truths.append(label)
            predictions.append(pred)

    pp.pprint(
        report(truths, predictions),
        sort_dicts=False,
    )


if __name__ == '__main__':
    run()
