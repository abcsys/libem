import random

import libem
from libem.tune import learn, check
from libem.prepare.datasets import amazon_google
from libem.core.log import header

from libem.match.prompt import rule as match_rule_prompt
from libem.match.prompt import experience as match_experience_prompt

calibrate = libem.toolchain("calibrate")


def main():
    num_iter = 1
    num_train_sample = 200
    num_test_sample = 400
    rnd = random.Random(43)

    match_model = "gpt-3.5-turbo"
    # match_model = "gpt-4o"
    learn_model = "gpt-4o"
    dataset = amazon_google

    libem.calibrate({
        "libem.match.parameter.model": match_model,
        "libem.tune.learn.parameter.model": learn_model,
        "libem.match.parameter.tools": [],  # turn off browse etc.
    }, verbose=True)

    print("Libem configurations:")
    calibrate.show()

    print(f"Match model: {match_model}; Learn model: {learn_model}")
    print(f"Load a dataset with {num_train_sample} samples")
    full_test_set = list(dataset.read_test())
    full_train_set = list(dataset.read_train())

    test_set = rnd.sample(
        full_test_set,
        num_test_sample
    )
    print(header("Test Libem before learn:"))
    before_test_scores = []
    before_test_score, before_mistakes = check(test_set)
    before_test_scores.append(before_test_score)
    print(f"Before learn: {len(before_mistakes)} mistakes\n "
          f"{before_mistakes}")
    print(f"Test scores: {before_test_score}")

    print(header("Start Learning"))
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
    print(header("End Learning"))

    print(header("Test again:"))
    test_score, mistakes = check(test_set)

    print(f"After learn: {len(mistakes)} mistake\n "
          f"{mistakes}")
    print(f"Test score: {test_score}")

    print(header("Summary"))
    print(f"Match model: {match_model}; "
          f"Learn model: {learn_model}")
    print(f"Number of mistakes: "
          f"before: {len(before_mistakes)}; "
          f"after: {len(mistakes)}")
    print(f"Train scores: {train_scores}")
    print(f"Test scores: {[before_test_score, test_score]}")


if __name__ == "__main__":
    main()
