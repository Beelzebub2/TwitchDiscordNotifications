import time
from colorama import Fore

debug = False


def performance_tracker(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        if debug:
            print(
                f"{Fore.LIGHTMAGENTA_EX}[PERFORMANCE] {Fore.LIGHTBLUE_EX}{func.__name__}{Fore.RESET} took {Fore.LIGHTYELLOW_EX}{execution_time:.4f}{Fore.RESET} seconds to execute.")
        return result
    return wrapper
