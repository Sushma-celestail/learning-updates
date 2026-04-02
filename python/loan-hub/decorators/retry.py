import time
import functools
import logging

logger = logging.getLogger(__name__)

def retry(max_attempts=3, delay=1):
    """
    Parameterized decorator for retrying a function call.
    Uses closures to capture max_attempts and delay.
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Attempt {attempts} failed for {func.__name__}: {e}")
                    if attempts == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts.")
                        raise
                    time.sleep(delay)
            return None
        return wrapper_retry
    return decorator_retry
