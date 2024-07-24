import random
import pprint as pp

import libem
from libem.prepare import datasets
from libem.tune.learn.icl import similar_shots
from libem.prepare.datasets import amazon_google as dataset
from libem.core.struct import Shots, Shot
from libem.match import prompt
from libem.core import eval


def run():
    random.seed(1)

    num_tests = 10
    num_shots = 3

    libem.calibrate({"libem.match.parameter.model": "gpt-3.5-turbo"})

    test_left, test_right, test_labels = \
        datasets.load(dataset.read_test(), num_tests)
    train_left, train_right, train_labels = \
        datasets.load(dataset.read_train())

    print("Before few-shot:")

    answers: list[dict] = libem.match(test_left, test_right)
    predictions = [1 if answer['answer'] == 'yes' else 0
                   for answer in answers]
    pp.pprint(
        eval.report(test_labels, predictions),
        sort_dicts=False,
    )

    libem.reset()
    print("After few-shot:")

    libem.calibrate({
        "libem.match.parameter.icl_strategy": similar_shots,
        "libem.match.parameter.num_shots": num_shots,
        "libem.match.prompt.shots": Shots([
            Shot(
                question=prompt.query(left=left, right=right),
                answer="yes" if label == 1 else "no"
            ) for left, right, label in zip(
                train_left, train_right, train_labels
            )
        ]),
    })

    answers: list[dict] = libem.match(test_left, test_right)
    predictions = [1 if answer['answer'] == 'yes' else 0
                   for answer in answers]
    pp.pprint(
        eval.report(test_labels, predictions),
        sort_dicts=False,
    )


if __name__ == '__main__':
    run()
