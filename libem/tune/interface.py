from libem.tune import func
from libem.tune.learn import func as learn_func


def tune(*args, **kwargs):
    return func(*args, **kwargs)


def learn(*args, **kwargs):
    return learn_func(*args, **kwargs)
