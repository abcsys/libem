import libem
from libem.core import model
import libem.core.util as libem_util
from libem.core.struct import Prompt

from libem.tune.learn import predict
from libem.tune.learn import prompt, parameter

import pprint as pp


def run(dataset, metric) -> tuple[float, Prompt.Rules, Prompt.Experiences]:
    preds, truths, mistakes, successes = predict(dataset)
    metric_func = libem_util.get_func(metric)
    score = metric_func(preds, truths)

    libem.info("[learn] metric:", metric, "score:", score)

    # if lots of mistakes, learn from rules
    rules, experiences = Prompt.Rules(), Prompt.Experiences()
    if score < 0.25:
        rules = rule_from_success(mistakes)
    else:
        experiences = experience_from_mistake(mistakes)
    return score, rules, experiences


def rule_from_success(successes: list) -> Prompt.Rules:
    libem.info("Successes: ", pp.pformat(successes))
    message = model.call(
        prompt=Prompt.join(
            prompt.recap_success(successes=successes),
            prompt.gen_rules(),
        ),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
        tools=[],
    )["output"]
    libem.info("Learned: ", message)
    rules = message.split("\n")
    return Prompt.Rules(rules)


def experience_from_mistake(mistakes: list) -> Prompt.Experiences:
    libem.info("Mistakes: ", pp.pformat(mistakes))
    message = model.call(
        prompt=Prompt.join(
            prompt.recap_mistake(mistakes=mistakes),
            prompt.gen_rules(),
        ),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
        tools=[],
    )["output"]
    libem.info("Learned: ", message)
    mistakes = message.split("\n")
    return Prompt.Experiences(mistakes)
