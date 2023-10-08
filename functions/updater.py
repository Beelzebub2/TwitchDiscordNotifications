from base64 import b64decode
import json
import time
import requests
import os
import shutil
from zipfile import ZipFile
from colorama import Fore, Style
import functions.Sql_handler
import functions.others

ch = functions.Sql_handler.SQLiteHandler("data.db")
current_version = ch.get_version()
var = functions.others.unpickle_variable()
console_width = var["console_width"]


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def set_console_title(title):
    system_type = os.name

    if system_type == "nt":
        os.system("title " + title)
    else:
        os.system("echo -ne '\033]0;" + title + "\007'")


online_version = "v" + \
    functions.others.get_version(
        "https://github.com/Beelzebub2/TwitchDiscordNotifications")


def search_for_updates():
    try:
        clear()
        set_console_title("Checking For Updates. . .")
        print(" " * console_width, end="\r")
        functions.others.log_print(
            f"{Fore.LIGHTYELLOW_EX}[INFO] Checking for updates")

        if online_version != current_version:
            set_console_title("New Update Found!")
            choice = input(
                f"{Fore.GREEN}[{Fore.YELLOW}>>>{Fore.GREEN}] {Fore.RESET}You want to update to the latest version? (Y to update): {Fore.RED}"
            )

            if choice.lower() == "y" or choice.lower() == "yes":
                print(f"{Fore.WHITE}\nUpdating. . .")
                set_console_title("Updating...")
                new = requests.get(
                    f"https://github.com/Beelzebub2/TwitchDiscordNotifications/archive/refs/heads/main.zip"
                )
                with open("TwitchDiscordNotifications.zip", "wb") as zipfile:
                    zipfile.write(new.content)
                with ZipFile("TwitchDiscordNotifications.zip", "r") as filezip:
                    filezip.extractall()
                os.remove("TwitchDiscordNotifications.zip")
                cwd = os.getcwd() + "\\TwitchDiscordNotifications-main"
                shutil.copytree(cwd, os.getcwd(), dirs_exist_ok=True)
                shutil.rmtree(cwd)
                ch.set_version(online_version)
                clear()
                set_console_title(f"Update Successfully Finished!")
                functions.others.log_print(
                    f"{Fore.LIGHTGREEN_EXGREEN}[SUCCESS] {Fore.LIGHTWHITE_EX}Updated bot from version {Fore.LIGHTYELLOW_EX + current_version + Fore.RESET} to { Fore.LIGHTGREEN_EX + online_version}")
                print("Attempting to start bot...")
                time.sleep(2)
                return True
    except KeyboardInterrupt:
        print(
            f"\n{Style.BRIGHT + Fore.LIGHTBLUE_EX}KeyboardInterrupt detected. Exiting gracefully.{Fore.RESET}"
        )
