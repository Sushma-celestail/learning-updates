import time
import functools
import logging

logger = logging.getLogger("loanhub")

def retry(max_attempts=3, delay=1):
    """
    Parameterized decorator for retrying a function on failure. (Day 3 Requirement)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Attempt {attempts} for {func.__name__} failed: {e}")
                    if attempts >= max_attempts:
                        raise e
                    time.sleep(delay)
        return wrapper
    return decorator
