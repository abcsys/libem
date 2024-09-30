import random
import pprint as pp

import libem
from libem.tune.learn.icl import similar_shots
from libem.prepare.datasets import amazon_google as dataset
from libem.optimize import profile
from libem.core.struct import Shots, Shot

from libem.match import prompt


def run():
    random.seed(1)

    num_tests = 30
    num_shots = 3

    libem.calibrate({"libem.match.parameter.model": "gpt-3.5-turbo"})

    print("Before few-shot:")

    pp.pprint(
        profile(dataset.read_test(), num_samples=num_tests),
        sort_dicts=False,
    )

    print("After few-shot:")

    libem.calibrate({
        "libem.match.parameter.icl_strategy": similar_shots,
        "libem.match.parameter.num_shots": num_shots,
        "libem.match.prompt.shots": Shots([
            Shot(
                question=prompt.query(left=d['left'], right=d['right']),
                answer="yes" if d['label'] == 1 else "no"
            ) for d in dataset.read_train()
        ]),
    })

    pp.pprint(
        profile(dataset.read_test(), num_samples=num_tests),
        sort_dicts=False,
    )


if __name__ == '__main__':
    run()
