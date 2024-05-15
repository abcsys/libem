import random

import libem
from libem.tune import learn, check
from libem.prepare.datasets import amazon_google
from libem.core.log import header

from libem.match.prompt import rule as match_rule_prompt
from libem.match.prompt import experience as match_experience_prompt

calibrate = libem.toolchain("calibrate")


def main():
    num_iter = 2
    num_train_sample = 100
    num_test_sample = 100
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
    full_test_set = list(amazon_google.read_test())
    full_train_set = list(amazon_google.read_train())

    test_scores = []
    test_set = rnd.sample(
        full_test_set,
        num_test_sample
    )
    test_score, mistakes = check(test_set)
    test_scores.append(test_score)

    train_scores = []
    for i in range(num_iter):
        print(header(f"Iteration {i + 1}"))

        train_set = rnd.sample(
            full_train_set,
            num_train_sample
        )

        score, learned_rule, learned_experience = \
            learn(train_set, "libem.core.eval.f1")

        print("Train score:", score)
        libem.calibrate({
            "libem.match.prompt.rule":
                match_rule_prompt() + learned_rule,
            "libem.match.prompt.experience":
                match_experience_prompt() + learned_experience,
        })
        train_scores.append(score)


    print(header("End of Learn Experiment"))

    print(header("Check the learned rule"))
    test_score, mistakes = check(test_set)
    test_scores.append(test_score)

    calibrate.show("libem.match")
    print(f"Train scores: {train_scores}")
    print(f"Test scores: {test_scores}")
    print(f"Mistakes: {len(mistakes)}")


if __name__ == "__main__":
    main()
