import time
from colorama import Fore
import threading

import psutil
from Functions import Json_config_hanldler
import Functions.others
import os
cwd = os.getcwd()
chj = Json_config_hanldler.JsonConfigHandler(
    os.path.join(cwd, "UI\\config.json"))
debug = chj.get_debug()


def performance_tracker(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        memory_before = psutil.virtual_memory().used

        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        memory_after = psutil.virtual_memory().used
        memory_diff = max(memory_after - memory_before,
                          0)  # Ensure non-negative

        if debug:
            args_str = f"{Fore.CYAN}Arguments: {args}, Keyword Arguments: {kwargs}{Fore.RESET}"
            memory_info = f"{Fore.MAGENTA}Memory Used: {memory_diff / (1024 * 1024):.2f} MB{Fore.RESET}"
            thread_info = f"{Fore.GREEN}Thread ID: {threading.current_thread().ident}{Fore.RESET}"

            Functions.others.log_print(
                f"{Functions.others.get_timestamp()} {Fore.LIGHTMAGENTA_EX}[PERFORMANCE] {Fore.LIGHTBLUE_EX}{func.__name__}{Fore.RESET} took {Fore.LIGHTYELLOW_EX}{Functions.others.format_elapsed_time(execution_time)} {Fore.RESET}", log_file_name="Performance_debug.txt", show_message=False)
            Functions.others.log_print(
                args_str, log_file_name="Performance_debug.txt", show_message=False)
            Functions.others.log_print(
                memory_info, log_file_name="Performance_debug.txt", show_message=False)
            Functions.others.log_print(
                thread_info, log_file_name="Performance_debug.txt", show_message=False)
            Functions.others.log_print(
                "\n", log_file_name="Performance_debug.txt", show_message=False)

        return result

    return wrapper


def run_in_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(
            target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()

    return wrapper
