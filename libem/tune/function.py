import random
import libem
from libem.tune.learn.function import learn, check
from libem.core.log import header

from libem.match.prompt import rule as match_rule_prompt

calibrate = libem.calibrate
random.seed = libem.LIBEM_SEED

schema = {}

def func(train_set: list, test_set: list,
         num_train_sample: int=100,
         num_test_sample: int=100,
         student_model: str='gpt-4o',
         teacher_model: str='gpt-4o',
         num_iter: int=2):
    
    # set config
    libem.calibrate({
        "libem.match.parameter.tools": [],  # turn off sub-tools
        "libem.match.parameter.model": student_model,
        "libem.tune.learn.parameter.model": teacher_model,
    })
    
    test_scores = []
    
    libem.info(header(f"Tool: Tune - Start"))

    sampled_test = random.sample(test_set, num_test_sample)
    test_score, mistakes = check(sampled_test)
    test_scores.append(test_score)

    train_scores = []
    for i in range(num_iter):
        libem.info(header(f"Tool: Tune - Iteration {i + 1}"))
        
        sampled_train = random.sample(train_set, num_train_sample)

        score, learned_rule = \
            learn(sampled_train, "libem.core.eval.f1")

        print("Train score:", score)
        libem.calibrate({
            "libem.match.prompt.rule":
                match_rule_prompt() + learned_rule,
        })
        libem.info(header(f"Tool: Tune - Train score: {score}"))
        train_scores.append(score)
    
    test_score, mistakes = check(sampled_test)
    test_scores.append(test_score)
    
    calibrate.show("libem.match")
    print(f"Tool: Tune - End")
    print(f"Tool: Tune - Test scores: {test_scores}")
    print(f"Tool: Tune - Mistakes: {len(mistakes)}")
