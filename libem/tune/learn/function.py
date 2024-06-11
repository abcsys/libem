import typing

from libem.tune.learn import parameter

from libem.tune.learn.strategy import (
    random_shots,
    similar_shots,
    attentive_shots,
    rule_from_mistakes,
)

schema = {}


def func(*args, **kwargs):
    return learn(*args, **kwargs)


def learn(dataset: list | typing.Iterable,
          metric: str = "libem.core.eval.f1",
          ):
    strategy = parameter.strategy()
    match strategy:
        case "random-shots":
            return random_shots.run(dataset, metric)
        case "similar-shots":
            return similar_shots.run(dataset, metric)
        case "rule-from-mistake":
            return rule_from_mistakes.run(dataset, metric)
        case "attentive-shots":
            return attentive_shots.run(dataset, metric)
        case _:
            raise ValueError(f"Invalid strategy: {strategy}")
