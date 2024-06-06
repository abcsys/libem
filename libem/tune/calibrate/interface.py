import pprint

from libem.tune.calibrate.function import collect, flatten


def export(toolchain="libem", nest=True):
    params = collect(toolchain)
    if nest:
        return params
    else:
        return flatten(params)


def show(*args, pretty=True, **kwargs):
    params = export(*args, **kwargs)
    if pretty:
        pp = pprint.PrettyPrinter(sort_dicts=False)
        pp.pprint(params)
    else:
        print(params)
