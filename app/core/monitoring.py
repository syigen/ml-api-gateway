from fastapi import APIRouter, FastAPI
from functools import wraps
import time
import asyncio


def timeit(func):
    @wraps(func)
    async def async_timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Async Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    @wraps(func)
    def sync_timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Sync Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_timeit_wrapper
    else:
        return sync_timeit_wrapper





