import requests
import os
import shutil
from zipfile import ZipFile
from colorama import Fore, Style
import Functions.Sql_handler
import Functions.others
from Functions.Json_config_hanldler import JsonConfigHandler
from urllib3.exceptions import MaxRetryError

ch = Functions.Sql_handler.SQLiteHandler()
cwd = os.getcwd()
chj = JsonConfigHandler(os.path.join(cwd, "UI\\config.json"))


def search_for_updates(autoupdate=False):
    try:
        current_version = ch.get_version()
        online_version = Functions.others.get_version()
        Functions.others.set_console_title("Checking For Updates. . .")
        if online_version != current_version:
            Functions.others.set_console_title(
                f"New Update Found! New Version:{online_version}")
            if autoupdate:
                try:
                    new = requests.get(
                        'https://github.com/Beelzebub2/TwitchDiscordNotifications/archive/refs/heads/main.zip')
                except requests.exceptions.ConnectTimeout or MaxRetryError:
                    Functions.others.log_print(
                        f"{Functions.others.get_timestamp()}{Functions.others.holders(2)}Failed to download update", show_message=False)
                    return False

                with open("TwitchDiscordNotifications.zip", "wb") as zipfile:
                    zipfile.write(new.content)
                with ZipFile("TwitchDiscordNotifications.zip", "r") as filezip:
                    filezip.extractall()
                os.remove("TwitchDiscordNotifications.zip")
                cwd = os.getcwd() + "\\TwitchDiscordNotifications-main"
                shutil.copytree(cwd, os.getcwd(), dirs_exist_ok=True)
                shutil.rmtree(cwd)
                ch.set_version(online_version)
                chj.set_version(online_version)
                Functions.others.clear_console()
                Functions.others.set_console_title(
                    f"Update Successfully Finished!")
                Functions.others.log_print(
                    f"{Functions.others.get_timestamp()} {Fore.LIGHTGREEN_EX}{Functions.others.holders(1)}{Fore.LIGHTWHITE_EX}Updated bot from version {Fore.LIGHTYELLOW_EX + current_version + Fore.RESET} to { Fore.LIGHTGREEN_EX + online_version}"
                )
                return (True, current_version, online_version)
            else:
                return False
        else:
            return False
    except KeyboardInterrupt:
        print(
            f"\n{Style.BRIGHT + Fore.LIGHTBLUE_EX}KeyboardInterrupt detected. Exiting gracefully.{Fore.RESET}"
        )
