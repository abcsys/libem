import importlib
from pydantic import create_model, Field
from typing import Dict


def toolchain(path):
    if not path.startswith("libem"):
        path = f"libem.{path}"
    return importlib.import_module(path)


chain = toolchain


def get_func(full_path):
    try:
        # Split the path to separate the module path from the function name
        module_path, function_name = full_path.rsplit('.', 1)
    except ValueError as e:
        raise Exception(f"Invalid input. Ensure you include "
                        f"a module path and function name: {e}")

    try:
        # Dynamically import the module
        module = importlib.import_module(module_path)
        # Retrieve the function or method by name
        function = getattr(module, function_name)
        return function
    except ImportError as e:
        raise Exception(f"Failed to import module: {e}")
    except AttributeError as e:
        raise Exception(f"Module '{module_path}' does not have "
                        f"a function named '{function_name}': {e}")

def create_json_schema(name: str, extra_fields={}, **fields):
    '''
    input:
        name: name of JSON object
        extra_fields: extra JSON fields to be appended alongside the schema
        fields: object fields in the format {<field_name>: <type>}
                or {<field_name>: (<type>, <description>)}
    output:
        a dict containing the schema in JSON form
    '''
    
    formatted_fields: Dict[str, Field] = {}
    
    for f_name, f_def in fields.items():
        if isinstance(f_def, tuple):
            try:
                f_type, f_desc = f_def
            except ValueError as e:
                raise Exception("Field definitions should be "
                                "in the format (<type>, <description>)")
        else:
            f_type, f_desc = f_def, None
        
        formatted_fields[f_name] = (f_type, Field(description=f_desc))
    
    schema = create_model(name, **formatted_fields).model_json_schema()
    schema.update(extra_fields)
    
    return schema
