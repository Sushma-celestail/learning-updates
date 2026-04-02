import time
import functools
import logging

logger = logging.getLogger(__name__)

def timer(func):
    """Decorator to measure and log function execution time."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return result
    return wrapper_timer

def async_timer(func):
    """Decorator to measure and log async function execution time."""
    @functools.wraps(func)
    async def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return result
    return wrapper_timer
