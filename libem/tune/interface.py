from libem.tune.learn import func
from libem.tune.learn import check as check_func


def learn(*args, **kwargs):
    return func(*args, **kwargs)


def check(*args, **kwargs):
    return check_func(*args, **kwargs)
