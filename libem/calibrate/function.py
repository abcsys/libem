import importlib

import libem
from libem.core.struct import Parameter

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
        libem.info(f"Tool: calibrate - {config}")
