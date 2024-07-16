import asyncio
from typing import List, Coroutine
from tqdm.asyncio import tqdm

import libem


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
