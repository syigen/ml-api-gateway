import asyncio
import time
from functools import wraps


def timeit(func):
    """
    Monitoring Utilities

    This module provides utility functions for monitoring and measuring the performance of
    asynchronous and synchronous functions.

    It contains decorators that can be used to measure the execution time of functions and
    print the results to the console.
    """

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
