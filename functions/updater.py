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

var = functions.others.unpickle_variable()
console_width = var["console_width"]


def search_for_updates(autoupdate=False):
    try:
        current_version = ch.get_version()
        online_version = "v" + \
            functions.others.get_version(
                "https://github.com/Beelzebub2/TwitchDiscordNotifications")
        functions.others.set_console_title("Checking For Updates. . .")
        print(" " * console_width, end="\r\r")

        if online_version != current_version:
            functions.others.set_console_title("New Update Found!")
            if not autoupdate:
                choice = input(
                    f"{Fore.GREEN}[{Fore.YELLOW}>>>{Fore.GREEN}] {Fore.RESET}You want to update to the latest version? (Y to update): {Fore.RED}"
                )

                if choice.lower() == "y" or choice.lower() == "yes":
                    print(f"{Fore.WHITE}\nUpdating. . .")
                    functions.others.set_console_title("Updating...")
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
                    functions.others.clear_console()
                    functions.others.set_console_title(
                        f"Update Successfully Finished!")
                    functions.others.log_print(
                        f"{Fore.LIGHTGREEN_EX}[SUCCESS] {Fore.LIGHTWHITE_EX}Updated bot from version {Fore.LIGHTYELLOW_EX + current_version + Fore.RESET} to { Fore.LIGHTGREEN_EX + online_version}")
                    print("Attempting to start bot...")
                    time.sleep(2)
                    return (True, current_version, online_version)
            if autoupdate:
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
                functions.others.clear_console()
                functions.others.set_console_title(
                    f"Update Successfully Finished!")
                functions.others.log_print(
                    f"{Fore.LIGHTGREEN_EX}[SUCCESS] {Fore.LIGHTWHITE_EX}Updated bot from version {Fore.LIGHTYELLOW_EX + current_version + Fore.RESET} to { Fore.LIGHTGREEN_EX + online_version}")
                return (True, current_version, online_version)
        else:
            return False
    except KeyboardInterrupt:
        print(
            f"\n{Style.BRIGHT + Fore.LIGHTBLUE_EX}KeyboardInterrupt detected. Exiting gracefully.{Fore.RESET}"
        )
