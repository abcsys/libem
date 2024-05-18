import math
import typing
import random

import libem
from libem.core import model
import libem.core.util as libem_util
from libem.core.struct import Prompt
from libem.tune.learn import prompt, parameter

random.seed(libem.LIBEM_SEED)

schema = {}


def func(*args, **kwargs):
    return learn(*args, **kwargs)


def predict(dataset) -> tuple[list, list, list, list]:
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


def learn(dataset: list | typing.Iterable,
          metric: str = "libem.core.eval.f1") -> tuple[float, Prompt.Rule]:
    preds, truths, mistakes, successes = predict(dataset)
    metric_func = libem_util.get_func(metric)
    score = metric_func(preds, truths)

    libem.info("Tool: learn - metric:", metric, "score:", score)
    
    # sample 0.15 * len(dataset) results to generate 
    # rulesets from, prioritizing 2-1 split of mistakes and successes
    mistakes_to_sample = min(len(mistakes), math.ceil(0.1 * len(dataset)))
    successes_to_sample = min(len(successes), math.ceil(0.15 * len(dataset) - mistakes_to_sample))
    sampled_set = random.sample(successes, k=successes_to_sample)
    sampled_set.extend(random.sample(mistakes, k=mistakes_to_sample))
    
    libem.info(f"Tool: learn - generating ruleset from "
               f"{mistakes_to_sample} mistakes and {successes_to_sample} successes")
    
    rule = rule_from_results(sampled_set)
    return score, rule


def rule_from_results(results: list) -> Prompt.Experience:
    message = model.call(
        prompt=Prompt.join(
            prompt.recap_results(results=results),
            prompt.gen_rules(),
        ),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
        tools=[],
    )
    libem.info("Learned: ", message)
    rules = message.split("\n")
    return Prompt.Rule(rules)


def check(dataset, metric: str = "libem.core.eval.f1") -> tuple[float, list, list]:
    preds, truths, mistakes, successes = predict(dataset)
    metric_func = libem_util.get_func(metric)
    score = metric_func(preds, truths)

    libem.info("Tool: check - metric:", metric, "score:", score)
    return score, mistakes
