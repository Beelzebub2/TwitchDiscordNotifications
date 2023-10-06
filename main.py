import asyncio
import datetime
import pickle
import signal
import shutil
import time
import os
import aiohttp
import requests
import discord
from colorama import init, Fore
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import concurrent.futures
from functions.configHandler import ConfigHandler
from functions.Sql_handler import SQLiteHandler
import functions.others

load_dotenv()


def main():
    async def check_stream(session, streamer_name):
        if not streamer_name:
            return False

        params = {
            "user_login": streamer_name,
        }

        async with session.get(
            API_BASE_URL, headers=HEADERS, params=params
        ) as response:
            if response.status == 200:
                data = await response.json()

                if "data" in data and len(data["data"]) > 0:
                    if streamer_name.lower() not in processed_streamers:
                        asyncio.create_task(
                            send_notification(streamer_name.strip(), data)
                        )
                        processed_streamers.append(streamer_name.lower())
                    return True
                if streamer_name.lower() in processed_streamers:
                    processed_streamers.remove(streamer_name.lower())

            return False

    async def send_notification(streamer_name, data):
        streamer_lists = ch.get_user_ids_with_streamers()
        for user_id, streamers in streamer_lists.items():
            try:
                member = await bot.fetch_user(int(user_id))
                if member:
                    dm_channel = member.dm_channel
                    if dm_channel is None:
                        dm_channel = await member.create_dm()
                    for streamer in streamers:
                        if streamer_name == streamer.strip():
                            embed = discord.Embed(
                                title=f"{streamer_name} is streaming!",
                                description=f"Click [here](https://www.twitch.tv/{streamer_name}) to watch the stream.",
                                color=discord.Color.green(),
                                timestamp=datetime.datetime.now()
                            )
                            if "data" in data and len(data["data"]) > 0:
                                stream_data = data["data"][0]
                                started_at = stream_data["started_at"]
                                user_id = stream_data["user_id"]
                                user_url = (
                                    f"https://api.twitch.tv/helix/users?id={user_id}"
                                )
                                if (
                                    "game_name" in stream_data
                                    and stream_data["game_name"]
                                ):
                                    game = stream_data["game_name"]
                                    embed.add_field(name="Game", value=game)

                                title = stream_data["title"]
                                viewers = stream_data["viewer_count"]
                                if int(viewers) == 0:
                                    embed.add_field(
                                        name="Viewers",
                                        value="No viewers. Be the first!",
                                    )
                                else:
                                    embed.add_field(
                                        name="Viewers", value=viewers)
                                user_response = requests.get(
                                    user_url, headers=HEADERS)
                                user_data = user_response.json()
                                profile_picture_url = user_data["data"][0][
                                    "profile_image_url"
                                ]
                                profile_picture_url = profile_picture_url.replace(
                                    "{width}", "300"
                                ).replace("{height}", "300")
                                start_time_str = functions.others.generate_timestamp_string(
                                    started_at)
                                embed.add_field(
                                    name="Stream Title", value=title)
                                embed.set_thumbnail(url=profile_picture_url)
                                embed.set_footer(
                                    text=f"{VERSION} | Made by Beelzebub2")
                                mention = f"||{member.mention}||"
                                embed.add_field(
                                    name="Stream Start Time (local)",
                                    value=start_time_str,
                                )
                                try:
                                    await dm_channel.send(mention, embed=embed)
                                    print(" " * console_width, end="\r")
                                    functions.others.log_print(
                                        Fore.CYAN
                                        + functions.others.get_timestamp()
                                        + Fore.RESET
                                        + " "
                                        + Fore.LIGHTGREEN_EX
                                        + f"Notification sent successfully for {Fore.CYAN + streamer_name + Fore.RESET}. {Fore.LIGHTGREEN_EX}to member {Fore.LIGHTCYAN_EX + member.name + Fore.RESET}"
                                    )
                                except discord.errors.Forbidden:
                                    print(" " * console_width, end="\r")
                                    functions.others.log_print(
                                        Fore.CYAN
                                        + functions.others.get_timestamp()
                                        + Fore.RESET
                                        + " "
                                        + f"Cannot send a message to user {member.name}. Missing permissions or DMs disabled."
                                    )
                            else:
                                print(" " * console_width, end="\r")
                                functions.others.log_print(
                                    Fore.CYAN
                                    + functions.others.get_timestamp()
                                    + Fore.RESET
                                    + " "
                                    + f"{streamer_name} is not streaming."
                                )
                                processed_streamers.remove(streamer_name)
            except discord.errors.NotFound:
                print(" " * console_width, end="\r")
                functions.others.log_print(
                    Fore.CYAN
                    + functions.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.RED
                    + f"User with ID {user_id} not found."
                    + Fore.RESET
                )

    @bot.event
    async def on_ready():
        ch.save_time(str(datetime.datetime.now()))
        if not ch.check_restart_status():
            bot_owner_id = ch.get_bot_owner_id()
            if not bot_owner_id:
                bot_info = await bot.application_info()
                owner_id = str(bot_info.owner.id)
                ch.save_bot_owner_id(owner_id)
                owner = bot.get_user(int(owner_id))
            else:
                owner = bot.get_user(int(bot_owner_id))
            embed = discord.Embed(
                title="Initialization Successful",
                description="Bot started successfully.",
                color=0x00FF00,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
            embed.add_field(name="Loaded commands", value=len(Loaded_commands))
            embed.add_field(name="Failed commands",
                            value="\n".join(Failed_commands))
            await owner.send(embed=embed)
        functions.others.clear_console()
        functions.others.set_console_title("TwitchDiscordNotifications")
        print(" " * console_width, end="\r")
        functions.others.log_print(
            Fore.CYAN
            + functions.others.get_timestamp()
            + Fore.RESET
            + Fore.LIGHTGREEN_EX
            + f" Running as {Fore.LIGHTCYAN_EX + bot.user.name + Fore.RESET}"
        )
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="Mention me to see my prefix"
        )
        await bot.change_presence(activity=activity)

        while True:
            start_time = time.time()
            print(" " * console_width, end="\r")
            print(
                "\033[K"
                + Fore.CYAN
                + functions.others.get_timestamp()
                + Fore.RESET
                + " "
                + Fore.LIGHTYELLOW_EX
                + "Checking"
                + Fore.RESET,
                end="\r",
            )

            streamers = ch.get_all_streamers()
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(
                    *[check_stream(session, streamer) for streamer in streamers]
                )

            end_time = time.time()
            elapsed_time = end_time - start_time

            if len(processed_streamers) != 0:
                print(" " * console_width, end="\r")
                print(
                    Fore.CYAN
                    + functions.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTGREEN_EX
                    + f"Currently streaming (Time taken: {elapsed_time:.2f} seconds): "
                    + Fore.RESET
                    + Fore.LIGHTWHITE_EX
                    + str(processed_streamers)
                    + Fore.RESET,
                    end="\r",
                )
            else:
                print(" " * console_width, end="\r")
                print(
                    Fore.CYAN
                    + functions.others.get_timestamp()
                    + Fore.RESET
                    + Fore.LIGHTWHITE_EX
                    + f" Checked {len(streamers)} streamers. Time taken: {elapsed_time:.2f} seconds"
                    + Fore.RESET,
                    end="\r",
                )

            await asyncio.sleep(5)


def create_env():
    if os.path.exists(".env"):
        return
    if CLIENT_ID and AUTHORIZATION and TOKEN:
        return

    if "REPLIT_DB_URL" in os.environ:
        if CLIENT_ID is None or AUTHORIZATION is None or TOKEN is None:
            print("Running on Replit")

    if "DYNO" in os.environ:
        if CLIENT_ID is None or AUTHORIZATION is None or TOKEN is None:
            print("Running on Heroku")

    env_keys = {
        "client_id": "Your Twitch application client id",
        "authorization": "Your Twitch application authorization token",
        "token": "Your discord bot token",
    }
    with open(".env", "w") as env_file:
        for key, value in env_keys.items():
            env_file.write(f"{key}={value}\n")

    if os.path.exists(".env"):
        print(
            "Secrets missing! created successfully please change filler text on .env or host secrets"
        )
        os._exit(0)


async def load_extension(filename):
    try:
        await bot.load_extension(f'commands.{filename[:-3]}')
        return f"Loaded {filename}"
    except Exception as e:
        return f"Failed to load {filename}: {e}"


async def load_extensions():
    extension_files = [filename for filename in os.listdir(
        './commands') if filename.endswith('.py')]
    workers = len(extension_files) + 1
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = await asyncio.gather(*[load_extension(filename) for filename in extension_files])

    end_time = time.time()
    elapsed_time = end_time - start_time
    for result in results:
        print(result)
        parts = result.split(" ")
        if len(parts) >= 2 and parts[0] == "Loaded":
            Loaded_commands.append(result)
        else:
            result = result.split(":")
            Failed_commands.append(result[0])

    print(f"Elapsed time: {elapsed_time:.4f} seconds")


async def get_custom_prefix(bot, message):
    if message.guild:
        guild_id = message.guild.id
        custom_prefix = ch.get_guild_prefix(guild_id)
        if custom_prefix:
            return custom_prefix
    return ch.get_prefix()


async def loadAndStart():
    async with bot:
        try:
            await load_extensions()
            await bot.start(TOKEN)
        except discord.errors.PrivilegedIntentsRequired:
            functions.others.clear_console()
            print(
                Fore.LIGHTRED_EX
                + "[INTENTS ERROR] "
                + Fore.LIGHTYELLOW_EX
                + "Please grant all the intents to your bot on https://discord.com/developers/applications/YourBotId/bot"
                + Fore.RESET
            )
            os._exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, functions.others.custom_interrupt_handler)
    CLIENT_ID = os.environ.get("client_id")
    AUTHORIZATION = os.environ.get("authorization")
    TOKEN = os.environ.get("token")
    repo_url = "https://github.com/Beelzebub2/TwitchDiscordNotifications"
    VERSION = "v" + functions.others.get_version(repo_url)
    create_env()
    ch = SQLiteHandler("data.db")
    ch.set_prefix(",")
    ch.set_version(VERSION)
    intents = Intents.all()
    intents.dm_messages = True
    Loaded_commands = []
    Failed_commands = []
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(ch.get_prefix()), intents=intents
    )
    try:
        console_width = shutil.get_terminal_size().columns
    except AttributeError:
        console_width = 80
    bot.command_prefix = get_custom_prefix
    bot.remove_command("help")  # delete default help command
    if ch.check_restart_status():
        processed_streamers = ch.processed_streamers
    else:
        processed_streamers = []
    API_BASE_URL = "https://api.twitch.tv/helix/streams"
    VERSION = ch.get_version()
    HEADERS = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {AUTHORIZATION}",
    }

    date_format = "%Y-%m-%d %H:%M:%S.%f"
    shared_variables = {
        "console_width": console_width,
        "processed_streamers": processed_streamers,
        "version": VERSION,
        "authorization": AUTHORIZATION,
        "client_id": CLIENT_ID,
        "date_format": date_format,
        "loaded_commands": Loaded_commands,
        "failed_commands": Failed_commands,
        "intents": intents,
        "headers": HEADERS
    }

    with open("variables.pkl", "wb") as file:
        pickle.dump(shared_variables, file)

    init()
    main()
    asyncio.run(loadAndStart())
