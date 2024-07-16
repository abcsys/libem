import asyncio
import importlib
from typing import List, Coroutine
from tqdm.asyncio import tqdm

import libem


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


async def proc_async_tasks(
        tasks: List[Coroutine],
        max_async_tasks: int = libem.LIBEM_MAX_ASYNC_TASKS,
        desc: str = "Processing Tasks") -> List:
    ''' Run async tasks under na imposed max concurrent tasks. '''

    sem = asyncio.Semaphore(max_async_tasks)

    async def _run(sem, task):
        async with sem:
            return await task

    futures = [
        asyncio.ensure_future(_run(sem, task))
        for task in tasks
    ]

    return await tqdm.gather(*futures, desc=desc)


def run_async_task(task: Coroutine):
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # Ensure the coroutine runs in the current loop
            return asyncio.ensure_future(task)
        elif loop.is_closed():
            # If the loop is closed, create a new event loop
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(task)
        else:
            return asyncio.run(task)
    except RuntimeError:
        # No running event loop
        return asyncio.run(task)
