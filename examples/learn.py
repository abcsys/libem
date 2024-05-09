import random

import libem
from libem.tune import learn, check
from libem.prepare.datasets import amazon_google
from libem.core.log import header

from libem.match.prompt import rule as match_rule
from libem.match.prompt import experience as match_experience

calibrate = libem.toolchain("calibrate")


def main():
    num_iter = 3
    num_train_sample = 20
    rnd = random.Random(42)
    print("Calibrate the match to use no tool")
    libem.calibrate({
        "libem.match.parameter.tools": [],  # turn off sub-tools
        "libem.match.parameter.model": "gpt-3.5-turbo",  # use GPT-3.5-turbo to train
    }, verbose=True)

    print("Libem configurations:")
    calibrate.show()
    print(header("Start of Learn Experiment"))

    print(f"Load a dataset with {num_train_sample} samples")
    dataset = rnd.sample(list(amazon_google.read_train()), num_train_sample)

    for i in range(num_iter):
        print(header(f"Iteration {i + 1}"))

        learned_rule, learned_experience = learn(dataset, "libem.core.eval.f1")

        print("Learned rules:", learned_rule)
        print("Learned experiences:", learned_experience)

        libem.calibrate({
            "libem.match.prompt.rule": match_rule.add(learned_rule),
            "libem.match.prompt.experience": match_experience.add(learned_experience),
        })
        calibrate.show("libem.match")

    print(header("End of Learn Experiment"))

    print(header("Check the learned rule"))
    score, mistakes = check(dataset)


if __name__ == "__main__":
    main()
