import sys
import importlib
import pkgutil

import libem
from libem.core.struct import Parameter, Prompt

schema = {}


def func(config, verbose=False):
    for path, value in config.items():
        # Split the path into module and attribute parts
        module_path, _, attribute = path.rpartition('.')

        try:
            # Dynamically import the module
            module = importlib.import_module(module_path)

            # Get the parameter
            parameter = getattr(module, attribute)
        except:
            raise Exception(f"unable to find parameter {path}")
        assert isinstance(parameter, Parameter), f"invalid parameter {path}"

        parameter.update(value)

    if verbose:
        libem.info(f"[calibrate] {config}")


def collect(tool: str, depth=sys.maxsize,
            full_attr=False, tool_only=False,
            stringify=False) -> dict:
    """Collect all parameters in the tool as nested dict.
    depth: the maximum depth in module hierarchy to search for parameters.
    full_attr: whether to include all attributes of the parameters.
    tool_only: whether to include only the tool name in the output.
    stringify: whether to stringify the output.

    :return: a dictionary of parameters with flattened paths.
    """
    parameters = {}

    mod_tool = importlib.import_module(tool)
    mod_parameter = _import_or_none(f"{tool}.parameter")
    mod_prompt = _import_or_none(f"{tool}.prompt")

    # get all parameters in the tool
    if mod_parameter is not None and not tool_only:
        for p, v in mod_parameter.__dict__.items():
            if isinstance(v, Parameter):
                if "parameter" not in parameters:
                    parameters["parameter"] = {}
                parameters["parameter"][p] = str(v.export(full_attr))

    # get all prompts in the tool
    if mod_prompt is not None and not tool_only:
        for p, v in mod_prompt.__dict__.items():
            if isinstance(v, (Prompt, Prompt.Rules, Prompt.Experiences)):
                if "prompt" not in parameters:
                    parameters["prompt"] = {}
                parameters["prompt"][p] = str(v.export(full_attr))

    if depth > 0:
        for sub_mod_name, is_mod in _list_top_level_modules(mod_tool):
            if is_mod:
                parameters.update(collect(sub_mod_name, depth - 1,
                                          full_attr, tool_only))

    parameters = dict(parameters)
    if len(parameters) > 0 or tool_only:
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


def _list_top_level_modules(package):
    top_level_modules = []
    first_level = package.__name__ + '.'
    length_of_first_level = len(first_level.split('.'))

    for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                          prefix=package.__name__ + '.',
                                                          onerror=lambda x: None):
        if modname.count('.') < length_of_first_level:  # Check depth of the package/module
            top_level_modules.append((modname, ispkg))

    return top_level_modules
