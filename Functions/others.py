import re
import os
import datetime
import tempfile
from colorama import Fore
import sys
import pickle
import requests
import Utilities.custom_decorators
from Functions.Json_config_hanldler import JsonConfigHandler
from tzlocal import get_localzone


def pickle_variable(data, folder="TwitchDiscordNotifications", filename="variables.pkl"):
    """
    Pickle one or more variables and save them to a file with a default filename.

    Args:
        data: One or more variables to be pickled.
        folder (str, optional): The name of the folder where the pickle file will be saved.
            Default is 'TwitchDiscordNotifications'.
        filename (str, optional): The name of the pickle file to save the variables to.
            Default is 'variables.pkl'.

    Returns:
        None
    """
    temp_dir = tempfile.gettempdir()

    folder_path = os.path.join(temp_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


def unpickle_variable(folder="TwitchDiscordNotifications", filename="variables.pkl"):
    """
    Load a variable from a pickle file with a default filename and return it.

    Args:
        folder (str, optional): The name of the folder where the pickle file is located.
            Default is 'TwitchDiscordNotifications'.
        filename (str, optional): The name of the pickle file to load the variable from.
            Default is 'variables.pkl'.

    Returns:
        object: The unpickled variable.
    """
    temp_dir = tempfile.gettempdir()
    folder_path = os.path.join(temp_dir, folder)
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'rb') as file:
        loaded_data = pickle.load(file)
    return loaded_data


def log_print(message, log_file_name="log.txt", show_message=True):
    cwd = os.getcwd()
    chj = JsonConfigHandler(
        os.path.join(cwd, "UI\\config.json"))
    console_width = unpickle_variable()["console_width"]
    max_lines = chj.get_max_lines()
    log_file_name = os.path.join(cwd, f"Logs\\{log_file_name}")

    def remove_color_codes(text):
        color_pattern = re.compile(r"(\x1b\[[0-9;]*m)|(\033\[K)")
        return color_pattern.sub("", text)

    @Utilities.custom_decorators.run_in_thread
    def trim_log_file():
        try:
            with open(log_file_name, "r", encoding="utf-8") as original_file:
                lines = original_file.readlines()

            if len(lines) >= max_lines:
                lines_to_remove = len(lines) - max_lines + 1
                new_lines = lines[lines_to_remove:]
                with open(log_file_name, "w", encoding="utf-8") as updated_file:
                    updated_file.writelines(new_lines)

        except:
            pass

    original_stdout = sys.stdout

    if show_message:
        print(" " * console_width, end="\r")
        print(message)
    try:
        with open(log_file_name, "a", encoding="utf-8") as log_file:
            sys.stdout = log_file
            message_without_colors = remove_color_codes(message)
            print(message_without_colors)
        trim_log_file()
    finally:
        sys.stdout = original_stdout


def get_timestamp():
    now = datetime.datetime.now()
    timestr = now.strftime(f"%Y-%m-%d {Fore.LIGHTBLUE_EX}%H:%M:%S{Fore.RESET}")
    timestr = f"{Fore.YELLOW}[{Fore.RESET}{Fore.CYAN + timestr + Fore.RESET}{Fore.YELLOW}]{Fore.RESET}"
    return timestr


def get_current_timezone():
    current_timezone = get_localzone()
    return str(current_timezone)


def generate_timestamp_string(started_at):
    dt = datetime.datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    unix_timestamp = int(dt.timestamp())
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


def get_version(repo_url, from_file=False):
    if from_file:
        with open("README.md", "r") as file:
            readme_content = file.read()
    else:
        readme_url = f"{repo_url}/blob/main/README.md"
        response = requests.get(readme_url)
        if response.status_code == 200:
            readme_content = response.text
        else:
            return "Version not found"

    pattern = r"Version-v([\d.]+)"
    match = re.search(pattern, readme_content)

    if match:
        version = match.group(1)
        return version
    else:
        return "Version not found"


def get_changelog(repo_url):
    version = "v" + get_version(repo_url)

    if version is None:
        return "Changelog not found"

    raw_readme_url = f"{repo_url}/raw/main/README.md"
    response = requests.get(raw_readme_url)

    if response.status_code == 200:
        readme_content = response.text
    else:
        return "Changelog not found"

    changelog = ""
    version_found = False

    for line in readme_content.split('\n'):
        if line.startswith(f"### {version}"):
            version_found = True
        elif line.startswith("### v"):
            version_found = False

        if version_found:
            changelog += line + "\n"

    if changelog:
        # Remove the date and "### version" lines
        changelog = re.sub(r'\d{2}/\d{2}/\d{4}\n', '', changelog)
        changelog = re.sub(fr'###\s*{re.escape(version)}', '', changelog)
        return changelog.strip()
    else:
        return f"Changelog for version {version} not found"

# TODO Im way to lazy to change all the prints to use this i'll do it eventually


def holders(type):
    match type:
        case 1:
            return f"{Fore.LIGHTGREEN_EX} [SUCCESS] "
        case 2:
            return f"{Fore.LIGHTRED_EX} [ERROR] "
        case 3:
            return f"{Fore.LIGHTYELLOW_EX} [INFO] "


def format_elapsed_time(elapsed_time):
    if elapsed_time < 1:
        elapsed_time_ms = int(elapsed_time * 1000)
        return f"{elapsed_time_ms:2} ms"
    elif elapsed_time < 60:
        return f"{elapsed_time:.2f} seconds"
    else:
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        return f"{minutes:2} min {seconds:2} sec"


def get_current_pid():
    return os.getpid()
