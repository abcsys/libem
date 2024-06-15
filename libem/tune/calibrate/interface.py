import pprint

from libem.tune.calibrate.function import collect, flatten, unflatten


def export(toolchain="libem",
           nest=True, tool_only=False):
    params = collect(toolchain, tool_only=tool_only)
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
