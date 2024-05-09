import sys
import importlib
import pkgutil
from collections import defaultdict

from libem.tune.learn import func
from libem.core.struct import Parameter, Prompt
from libem.tune.learn.function import check as check_func


def learn(*args, **kwargs):
    return func(*args, **kwargs)


def check(*args, **kwargs):
    return check_func(*args, **kwargs)


def collect(tool: str, depth=sys.maxsize, is_full=False) -> dict:
    """Collect all parameters in the tool as nested dict.
    depth: the maximum depth in module hierarchy to search for parameters.
    is_full: whether to include all attributes of the parameters.

    :return: a dictionary of parameters with flattened paths.
    """
    parameters = defaultdict(dict)

    mod_tool = importlib.import_module(tool)
    mod_parameter = _import_or_none(f"{tool}.parameter")
    mod_prompt = _import_or_none(f"{tool}.prompt")

    # get all parameters in the tool
    if mod_parameter is not None:
        for p, v in mod_parameter.__dict__.items():
            if isinstance(v, Parameter):
                parameters["parameter"][p] = v.export(is_full)

    # get all prompts in the tool
    if mod_prompt is not None:
        for p, v in mod_prompt.__dict__.items():
            if isinstance(v, Prompt):
                parameters["prompt"][p] = v.export(is_full)

    if depth > 0:
        for _, sub_mod_name, is_mod in pkgutil.walk_packages(
                mod_tool.__path__,
                mod_tool.__name__ + "."):
            if is_mod:
                parameters.update(collect(sub_mod_name, depth - 1, is_full))

    parameters = dict(parameters)
    if len(parameters) > 0:
        return {tool.split(".")[-1]: parameters}
    else:
        return {}


def flatten(d, parent_key="", sep="."):
    """
    Flattens a nested dictionary, ensuring each leaf has a full path as its key.

    Args:
    - d (dict): The dictionary to flatten.
    - parent_key (str): The base path of the keys being processed (used recursively).
    - sep (str): The separator between key fragments in the path.

    Returns:
    - dict: A flat dictionary with paths as keys.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten(flat_dict, sep="."):
    """
    Unflattens a flat dictionary with paths as keys into a nested dictionary.

    Args:
    - flat_dict (dict): The dictionary to unflatten, with paths as keys.
    - sep (str): The separator used between key fragments in the path.

    Returns:
    - dict: A nested dictionary.
    """
    unflattened_dict = {}
    for composite_key, value in flat_dict.items():
        parts = composite_key.split(sep)
        d = unflattened_dict
        for part in parts[:-1]:  # go up to the second-to-last part
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return unflattened_dict


# unflatten alias
nest = unflatten


def _import_or_none(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        return None
