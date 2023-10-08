import concurrent.futures
import re
import os
import datetime
from colorama import Fore
import sys
import pickle
import requests


def pickle_variable(data, filename="variables.pkl"):
    """
    Pickle one or more variables and save them to a file with a default filename.

    Args:
        *args: One or more variables to be pickled.
        filename (str, optional): The name of the pickle file to save the variables to.
            Default is 'data.pkl'.

    Returns:
        None
    """
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def unpickle_variable(filename="variables.pkl"):
    """
    Load a variable from a pickle file with a default filename and return it.

    Args:
        filename (str, optional): The name of the pickle file to load the variable from.
            Default is 'data.pkl'.

    Returns:
        object: The unpickled variable.
    """
    with open(filename, 'rb') as file:
        loaded_data = pickle.load(file)
    return loaded_data


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
    timestr = now.strftime(f"%Y-%m-%d {Fore.LIGHTBLUE_EX}%H:%M:%S{Fore.RESET}")
    timestr = f"{Fore.YELLOW}[{Fore.RESET}{Fore.CYAN + timestr + Fore.RESET}{Fore.YELLOW}]{Fore.RESET}"
    return timestr


def generate_timestamp_string(started_at):
    started_datetime = datetime.datetime.fromisoformat(started_at.rstrip("Z"))
    unix_timestamp = int(started_datetime.timestamp()) + 3600
    timestamp_string = f"<t:{unix_timestamp}:T>"
    return timestamp_string


def set_console_title(title):
    variables = unpickle_variable()
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


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def get_version(repo_url):
    readme_url = f"{repo_url}/blob/main/README.md"
    response = requests.get(readme_url)
    if response.status_code == 200:
        readme_content = response.text
        pattern = r"Version-v([\d.]+)"
        match = re.search(pattern, readme_content)

        if match:
            version = match.group(1)
            return version
        else:
            return "Version not found"
    else:
        return f"Version not found"
