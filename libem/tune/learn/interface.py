from libem.tune.learn.function import (
    predict,
    check,
)

_ = predict, check

from libem.tune.learn.icl import (
    given_shots,
    similar_shots,
    random_shots,
    attentive_shots,
)

icl_strategies = {
    "given_shots": given_shots,
    "similar_shots": similar_shots,
    "random_shots": random_shots,
    "attentive_shots": attentive_shots,
}

icl_strategies.update({k.replace('_', '-'): v for k, v in icl_strategies.items()})



