import importlib
import jsonref
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

def create_json_schema(extra_fields: dict = {}, **fields) -> dict:
    '''
    input:
        extra_fields: extra JSON fields in dict form to be appended
                      at the root level of the the schema
        fields: object fields in the format {<field_name>: <type>}
                or {<field_name>: (<type>, <description>)};
                <type> can be a dict/list containing inner fields
    output:
        a dict containing the schema in JSON form
    '''
    
    def create_json_model(**fields):
        formatted_fields: Dict[str, Field] = {}
    
        for f_name, f_def in fields.items():
            f_desc = None
            if isinstance(f_def, tuple): # split type and description
                try:
                    f_def, f_desc = f_def
                except ValueError as e:
                    raise Exception("Field definitions should be "
                                    "in the format (<type>, <description>)")
            
            if isinstance(f_def, dict): # handle nested object
                f_type = create_json_model(**f_def)
            elif isinstance(f_def, list): # handle nested array of objects
                if len(f_def) != 1:
                    raise Exception("List fields should have exactly one type")
                f_type = list[create_json_model(**f_def[0])]
            else:
                f_type = f_def
            
            formatted_fields[f_name] = (f_type, Field(description=f_desc))
        
        return create_model(__model_name="", **formatted_fields)

    def merge_extra_fields(schema: dict, extra_fields: dict) -> dict:
        """
        Appends extra fields only when the schema contains both "properties" and "required" fields.
        Also removes the title field from all levels.
        """
        schema.pop("title", None)  # remove title from current level
        
        # check if both "properties" and "required" are present
        if "properties" in schema and "required" in schema:
            schema.update(extra_fields)  # merge extra fields at this level
            
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)  # remove title from all properties

        # recursively apply the logic to nested objects
        for key in schema.keys():
            if isinstance(schema[key], dict):
                schema[key] = merge_extra_fields(schema[key], extra_fields)

        return schema
    
    schema = jsonref.replace_refs(create_json_model(**fields).model_json_schema(), proxies=False)
    # remove the unnecessary $defs key generated from recursive calls and add extra fields
    schema.pop("$defs", None)
    return merge_extra_fields(schema, extra_fields)
