import time
import functools
import logging

logger = logging.getLogger("loanhub")

def timer(func):
    """
    Decorator to log the execution time of a function. (Day 3 Requirement)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(f"Function {func.__name__} took {duration:.4f} seconds to execute.")
        return result
    return wrapper
