from libem.tune import func
from libem.tune.learn.function import check as check_func


def tune(*args, **kwargs):
    return func(*args, **kwargs)


def check(*args, **kwargs):
    return check_func(*args, **kwargs)
