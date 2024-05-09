import pprint as pp

from libem.tune import collect, flatten


def export(toolchain="libem", nest=True):
    params = collect(toolchain)
    if nest:
        return params
    else:
        return flatten(params)


def show(*args, pretty=True, **kwargs):
    params = export(*args, **kwargs)
    if pretty:
        pp.pprint(params)
    else:
        print(params)
