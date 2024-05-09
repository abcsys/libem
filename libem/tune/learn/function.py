import typing
import pprint as pp

import libem
from libem.core import model
import libem.core.util as libem_util
from libem.core.struct import Prompt
from libem.tune.learn import prompt, parameter

schema = {}


def func(*args, **kwargs):
    return learn(*args, **kwargs)


def predict(dataset) -> (list, list, list, list):
    preds, truths = [], []
    mistakes, successes = [], []

    for i, record in enumerate(dataset):
        left, right, truth = record["left"], record["right"], record["label"]

        pred = libem.match(left, right)
        libem.info("Tool: learn - record:", i, "pred:", pred, "true:", truth)

        preds.append(1 if pred.lower() == "yes" else 0)
        truths.append(truth)

        truth = "yes" if truth == 1 else "no"
        outcome = {
            "entity 1": left,
            "entity 2": right,
            "your answer": pred,
            "true answer": truth,
        }

        if pred == truth:
            successes.append(outcome)
        else:
            mistakes.append(outcome)
    return preds, truths, mistakes, successes


def learn(dataset: list or typing.Iterable,
          metric: str = "libem.core.eval.f1") -> (Prompt.Rule, Prompt.Experience):
    preds, truths, mistakes, successes = predict(dataset)
    metric_func = libem_util.get_func(metric)
    score = metric_func(preds, truths)

    libem.info("Tool: learn - metric:", metric, "score:", score)

    # if lots of mistakes, learn from rules
    rule, experience = Prompt.Rule(), Prompt.Experience()
    if score < 0.25:
        rule = rule_from_success(mistakes)
    else:
        experience = experience_from_mistake(mistakes)
    return rule, experience


def rule_from_success(successes: list) -> Prompt.Rule:
    libem.info("Successes: ", pp.pformat(successes))
    message = model.call(
        prompt=Prompt.join(
            prompt.recap_success(successes=successes),
            prompt.gen_rules(),
        ),
        model=parameter.model(),
        temperature=parameter.temperature(),
        tools=[],
    )
    libem.info("Learned: ", message)
    rules = message.split("\n")
    return Prompt.Rule(rules)


def experience_from_mistake(mistakes: list) -> Prompt.Experience:
    libem.info("Mistakes: ", pp.pformat(mistakes))
    message = model.call(
        prompt=Prompt.join(
            prompt.recap_mistake(mistakes=mistakes),
            prompt.gen_rules(),
        ),
        model=parameter.model(),
        temperature=parameter.temperature(),
        tools=[],
    )
    libem.info("Learned: ", message)
    mistakes = message.split("\n")
    return Prompt.Experience(mistakes)


def check(dataset, metric: str = "libem.core.eval.f1") -> (float, list):
    preds, truths, mistakes, successes = predict(dataset)
    metric_func = libem_util.get_func(metric)
    score = metric_func(preds, truths)

    libem.info("Tool: check - metric:", metric, "score:", score)
    return score, mistakes
