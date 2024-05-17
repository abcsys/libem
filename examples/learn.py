import random

import libem
from libem.prepare.datasets import amazon_google
from libem.core.log import header

calibrate = libem.toolchain("calibrate")


def main():
    num_iter = 2
    num_train_sample = 100
    num_test_sample = 100
    match_model, learn_model = 'gpt-4-turbo', 'gpt-3.5-turbo'

    libem.calibrate({
        "libem.match.parameter.model": match_model,
        "libem.tune.learn.parameter.model": learn_model,
        "libem.match.parameter.tools": [],  # turn off browse etc.
    }, verbose=True)

    print("Libem configurations:")
    calibrate.show()
    print(f"Match model: {match_model}; Learn model: {learn_model}")
    print(f"Load a dataset with {num_train_sample} samples")
    
    full_test_set = list(amazon_google.read_test())
    full_train_set = list(amazon_google.read_train())
    random.shuffle(full_train_set)
    random.shuffle(full_test_set)
    
    libem.tune(train_set=full_train_set, test_set=full_test_set, 
               num_train_sample=num_train_sample, num_test_sample=num_test_sample,
               learn_model=learn_model, match_model=match_model,
               num_iter=num_iter)
    
    print(header("End of Learn Experiment"))


if __name__ == "__main__":
    main()
