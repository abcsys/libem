import asyncio
import importlib
from typing import Iterable
from tqdm.asyncio import tqdm

import libem

""" Toolchain utilities. """


def toolchain(path):
    if not path.startswith("libem"):
        path = f"libem.{path}"
    return importlib.import_module(path)


chain = toolchain


def get_func(full_path):
    try:
        # Split the path to separate the module path from the function name
        module_path, function_name = full_path.rsplit('.', 1)

        # Dynamically import the module
        module = importlib.import_module(module_path)
        # Retrieve the function or method by name
        function = getattr(module, function_name)
        return function
    except ValueError as e:
        raise Exception(f"Invalid input. Ensure you include a module path and function name: {e}")
    except ImportError as e:
        raise Exception(f"Failed to import module: {e}")
    except AttributeError as e:
        raise Exception(f"Module '{module_path}' does not have a function named '{function_name}': {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

async def async_run(tasks: Iterable,
                    max_concurrency: int = libem.LIBEM_MAX_ASYNC_TASKS):
    ''' Run all async tasks with an imposed max concurrent tasks limit. '''

    async def sem_run(sem, task):
        async with sem:
            return await task

    async def run():
        sem = asyncio.Semaphore(max_concurrency)
        futures = [asyncio.ensure_future(sem_run(sem, c)) 
                   for c in tasks]

        return await tqdm.gather(*futures)

    return await run()
