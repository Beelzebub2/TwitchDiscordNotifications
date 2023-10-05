import re
import os
import datetime
from colorama import Fore
import sys
import pickle


with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

def log_print(message, log_file_name="log.txt", max_lines=1000):
    def remove_color_codes(text):
        color_pattern = re.compile(r"(\x1b\[[0-9;]*m)|(\033\[K)")
        return color_pattern.sub("", text)

    def trim_log_file():
        try:
            with open(log_file_name, "r") as original_file:
                lines = original_file.readlines()

            if len(lines) >= max_lines:
                lines_to_remove = len(lines) - max_lines + 1
                new_lines = lines[lines_to_remove:]
                with open(log_file_name, "w") as updated_file:
                    updated_file.writelines(new_lines)

        except Exception as e:
            print(f"Error trimming log file: {e}")

    original_stdout = sys.stdout

    try:
        print(message)

        with open(log_file_name, "a") as log_file:
            sys.stdout = log_file
            message_without_colors = remove_color_codes(message)
            print(message_without_colors)
        trim_log_file()

    except Exception as e:
        sys.stdout = original_stdout
        print(f"Error logging to file: {e}")
    finally:
        sys.stdout = original_stdout

def get_timestamp():
    now = datetime.datetime.now()
    timestr = now.strftime("%Y-%m-%d %H:%M:%S")
    timestr = f"{Fore.YELLOW}[{Fore.RESET}{Fore.CYAN + timestr + Fore.RESET}{Fore.YELLOW}]{Fore.RESET}"
    return timestr

def set_console_title(title):
    if os.name == 'nt':
        try:
            os.system(f'title {title} {variables["version"]}')
        except Exception:
            pass
    else:
        try:
            os.system(f'printf "\033]0;{title} {variables["version"]}\007"')
        except Exception:
            pass

