import asyncio
import datetime
import requests
import os
import re
import discord
import traceback
from colorama import init, Fore, Style
from discord.ext import commands
from discord import Intents
from configparser import ConfigParser

intents = Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True  # Enable the messages intent
intents.guild_messages = True  # Enable the guild messages intent
intents.dm_messages = True  # Enable the direct message messages intent
processed_streamers = []
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace 'YOUR_CLIENT_ID' with your actual application id
CLIENT_ID = "YOUR_CLIENT_ID"

# Replace 'YOUR_AUTHORIZATION' with your actual application OAuth token
AUTHORIZATION = "YOUR_AUTHORIZATION"

# Replace 'YOUR_BOT_TOKEN' with your actual discord bot token
TOKEN = "YOUR_BOT_TOKEN"


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            tb = traceback.extract_tb(error.__traceback__)
            file = tb[-1].filename  # Extract the filename
            line = tb[-1].lineno
            error_message = f"An error occurred in {Fore.CYAN + Style.BRIGHT}{file}{Style.RESET_ALL}\n{Fore.CYAN + Style.BRIGHT}Line: {line}{Fore.RED} error: {error} {Style.RESET_ALL}"
            print(
                Fore.YELLOW
                + Style.BRIGHT
                + "\n"
                + error_message
                + "\n"
                + Style.RESET_ALL
            )

    return wrapper


@error_handler
def get_timestamp():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@error_handler
def read_config():
    PATH = os.path.dirname(os.path.realpath(__file__))
    Config_File = os.path.join(PATH, "user-list.ini")
    Config = ConfigParser()
    Config.read(Config_File)
    user_notifications = {}
    for user_id, streamers in Config["USER-LIST"].items():
        if user_id.lower().startswith("userid"):
            user_id = user_id.replace("userid", "").strip().lower()
            streamer_list = streamers.split(",")
            user_notifications[user_id] = streamer_list
    return user_notifications


@error_handler
def write_config(user_notifications):
    PATH = os.path.dirname(os.path.realpath(__file__))
    Config_File = os.path.join(PATH, "config.ini")
    Config = ConfigParser()
    Config.read(Config_File)

    # Update the existing config with the new user notifications
    for user_id, streamers in user_notifications.items():
        user_key = f"userId{user_id}"
        streamer_value = ", ".join(map(str.strip, streamers))
        Config.set("CONFIG", user_key, streamer_value)

    # Write the updated config to the file
    with open(Config_File, "w") as config_file:
        Config.write(config_file)


@error_handler
async def check_stream(streamer_name):
    if not streamer_name:
        return False

    endpoint = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {AUTHORIZATION}",
    }

    # Parameters for the API request
    params = {
        "user_login": streamer_name,
    }
    # Send GET request to Twitch API
    response = requests.get(endpoint, headers=headers, params=params)

    # Parse the JSON response
    data = response.json()

    # Check if the "data" key exists in the response
    if "data" in data:
        if len(data["data"]) > 0:
            if streamer_name not in processed_streamers:
                user_notifications = read_config()
                await send_notification(streamer_name.strip(), user_notifications)
                processed_streamers.append(streamer_name)
            return True
    else:
        print("Error: 'data' key not found in API response")

    if streamer_name in processed_streamers:
        processed_streamers.remove(streamer_name)
    return False


async def send_notification(streamer_name, user_notifications):
    for user_id, streamers in user_notifications.items():
        try:
            member = await bot.fetch_user(int(user_id))
            if member:
                dm_channel = member.dm_channel
                if dm_channel is None:
                    dm_channel = await member.create_dm()
                for streamer in streamers:
                    if streamer_name == streamer.strip():
                        url = f"https://api.twitch.tv/helix/streams?user_login={streamer_name}"
                        headers = {
                            "Client-ID": CLIENT_ID,
                            "Authorization": f"Bearer {AUTHORIZATION}",
                        }
                        response = requests.get(url, headers=headers)
                        data = response.json()
                        if "data" in data and len(data["data"]) > 0:
                            user_id = data["data"][0]["user_id"]
                            user_url = f"https://api.twitch.tv/helix/users?id={user_id}"
                            user_response = requests.get(user_url, headers=headers)
                            user_data = user_response.json()
                            profile_picture_url = user_data["data"][0][
                                "profile_image_url"
                            ]
                            profile_picture_url = profile_picture_url.replace(
                                "{width}", "300"
                            ).replace("{height}", "300")
                            embed = discord.Embed(
                                title=f"{streamer_name} is streaming!",
                                description=f"Click [here](https://www.twitch.tv/{streamer_name}) to watch the stream.",
                                color=discord.Color.green(),
                            )
                            embed.set_thumbnail(url=profile_picture_url)
                            embed.set_footer(text=f"v1.0 | Made by Beelzebub2")
                            try:
                                await dm_channel.send(embed=embed)
                                print(
                                    get_timestamp()
                                    + " "
                                    + f"Notification sent successfully for {streamer_name}."
                                )
                            except discord.errors.Forbidden:
                                print(
                                    get_timestamp()
                                    + " "
                                    + f"Cannot send a message to user {member.name}. Missing permissions or DMs disabled."
                                )
                        else:
                            print(
                                get_timestamp()
                                + " "
                                + f"{streamer_name} is not streaming."
                            )
        except discord.errors.NotFound:
            # Handle the case where the user is not found
            print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"User with ID {user_id} not found."
                + Fore.RESET
            )


@bot.event
async def on_ready():
    print(
        Fore.CYAN
        + get_timestamp()
        + Fore.RESET
        + " "
        + Fore.GREEN
        + f"Bot connected as {bot.user}"
        + Fore.RESET
    )
    user_notifications = read_config()
    streamers = []
    for streamer_list in user_notifications.values():
        streamers.extend(streamer_list)
    streamers = ", ".join(streamers)  # Join streamer names with a comma
    activity = discord.Activity(
        type=discord.ActivityType.watching, name="The streamers for you"
    )
    await bot.change_presence(activity=activity)

    while True:
        for streamer_list in user_notifications.values():
            for streamer_name in streamer_list:
                await check_stream(streamer_name.strip())
        if len(processed_streamers) != 0:
            print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.LIGHTWHITE_EX
                + str(processed_streamers)
                + Fore.RESET
            )
        await asyncio.sleep(20)


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        if message.content.lower().startswith("watch"):
            # Extract the streamer name from the message content
            streamer_name = message.content[6:].strip()

            if "https://www.twitch.tv/" in streamer_name:
                streamer_name = re.search(
                    r"https://www.twitch.tv/([^\s/]+)", streamer_name
                ).group(1)
            user_id = str(message.author.id)
            user_notifications = read_config()
            if user_id in user_notifications:
                streamer_list = user_notifications[user_id]
                if streamer_name.lower() not in [
                    s.lower().strip() for s in streamer_list
                ]:
                    streamer_list.append(streamer_name.strip())
                    write_config(
                        user_notifications
                    )  # Write the updated config to the file
                    print(
                        get_timestamp()
                        + " "
                        + Fore.GREEN
                        + f"Added {Fore.CYAN + streamer_name + Fore.RESET} to user {Fore.CYAN + message.author.name + Fore.RESET}'s watchlist."
                        + Fore.RESET
                    )
                    embed = discord.Embed(
                        title="Stream Watchlist",
                        description=f"Added {streamer_name} to your watchlist.",
                        color=65280,
                    )
                    embed.set_footer(text="v1.0 | Made by Beelzebub2")
                    await message.channel.send(embed=embed)
                    if streamer_name in processed_streamers:
                        processed_streamers.remove(streamer_name)
                else:
                    print(
                        get_timestamp()
                        + " "
                        + f"{Fore.CYAN + streamer_name + Fore.RESET} is already in user {Fore.CYAN + message.author.name + Fore.RESET}'s watchlist."
                    )
                    embed = discord.Embed(
                        title="Stream Watchlist",
                        description=f"{streamer_name} is already in your watchlist.",
                        color=16759808,
                    )
                    embed.set_footer(text="v1.0 | Made by Beelzebub2")
                    await message.channel.send(embed=embed)
            else:
                user_notifications[user_id] = [streamer_name.strip()]
                write_config(user_notifications)  # Write the updated config to the file
                print(
                    get_timestamp()
                    + " "
                    + Fore.GREEN
                    + f"Created a new watchlist for user {Fore.CYAN + message.author.name + Fore.RESET} and added {Fore.CYAN + streamer_name + Fore.RESET}."
                    + Fore.RESET
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description=f"Created a new watchlist for you and added {streamer_name}.",
                    color=65280,
                )
                embed.set_footer(text="v1.0 | Made by Beelzebub2")
                await message.channel.send(embed=embed)

        elif message.content.lower().startswith("unwatch"):
            # Extract the streamer name from the message content
            streamer_name = message.content.lower().split("unwatch")[1].strip()

            # Check if the message contains a Twitch profile link
            if "https://www.twitch.tv/" in streamer_name:
                streamer_name = re.search(
                    r"https://www.twitch.tv/([^\s/]+)", streamer_name
                ).group(1)

            user_id = str(message.author.id)
            user_notifications = read_config()
            if user_id in user_notifications:
                streamer_list = user_notifications[user_id]
                if streamer_name.lower() in [s.lower().strip() for s in streamer_list]:
                    # Remove the streamer from the watchlist
                    streamer_list = [
                        s.strip()
                        for s in streamer_list
                        if s.lower().strip() != streamer_name.lower()
                    ]
                    user_notifications[user_id] = streamer_list
                    write_config(
                        user_notifications
                    )  # Write the updated config to the file
                    print(
                        get_timestamp()
                        + " "
                        + Fore.GREEN
                        + f"Removed {Fore.CYAN + streamer_name + Fore.RESET} from user {Fore.CYAN + message.author.name + Fore.RESET}'s watchlist."
                        + Fore.RESET
                    )
                    embed = discord.Embed(
                        title="Stream Watchlist",
                        description=f"Removed {streamer_name} from your watchlist.",
                        color=65280,
                    )
                    embed.set_footer(text="v1.0 | Made by Beelzebub2")
                    await message.channel.send(embed=embed)
                else:
                    print(
                        get_timestamp()
                        + " "
                        + f"{Fore.CYAN + streamer_name + Fore.RESET} is not in user {Fore.CYAN + message.author.name + Fore.RESET}'s watchlist."
                    )
                    embed = discord.Embed(
                        title="Stream Watchlist",
                        description=f"{streamer_name} is not in your watchlist.",
                        color=16759808,
                    )
                    embed.set_footer(text="v1.0 | Made by Beelzebub2")
                    await message.channel.send(embed=embed)

        elif message.content.lower().startswith("help"):
            help_message = (
                "**Watch** streamername or streamer link - adds the streamer to your watchlist\n"
                "**Unwatch** streamername or streamer link - removes the streamer from your watchlist\n"
                "**Help** - shows list of commands\n"
                "**List** - Show your list of streamers\n"
                "**Clear** - Deletes all messages sent by the bot (1|1s)\n"
            )
            embed = discord.Embed(
                title="Stream Watchlist - Help",
                description=help_message,
                color=48639,
            )
            embed.set_footer(text="v1.0 | Made by Beelzebub2")
            await message.channel.send(embed=embed)

        elif message.content.lower().startswith("list"):
            user_id = str(message.author.id)
            user_notifications = read_config()
            if user_id in user_notifications:
                streamer_list = user_notifications[user_id]
                if streamer_list:
                    streamer_names = ", ".join(streamer_list)
                    print(
                        get_timestamp()
                        + " "
                        + Fore.GREEN
                        + f"{Fore.CYAN + message.author.name + Fore.RESET} requested their streamers: {Fore.CYAN + streamer_names + Fore.RESET}"
                        + Fore.RESET
                    )

                    embed = discord.Embed(
                        title="Your Streamers",
                        description=f"You are currently watching the following streamers:\n{streamer_names}",
                        color=10242047,
                    )
                    embed.set_footer(text="v1.0 | Made by Beelzebub2")

                    await message.channel.send(embed=embed)
                else:
                    print(
                        get_timestamp()
                        + " "
                        + Fore.YELLOW
                        + f"{Fore.CYAN + message.author.name + Fore.RESET} requested their streamers, but the watchlist is empty."
                        + Fore.RESET
                    )
                    embed = discord.Embed(
                        title="Stream Watchlist",
                        description="Your watchlist is empty.",
                        color=16759808,
                    )
                    embed.set_footer(text="v1.0 | Made by Beelzebub2")
                    await message.channel.send(embed=embed)
            else:
                print(
                    get_timestamp()
                    + " "
                    + Fore.RED
                    + f"{Fore.CYAN + message.author.name + Fore.RESET} requested their streamers, but they don't have a watchlist yet."
                    + Fore.RESET
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description="You don't have a watchlist yet.",
                    color=16711680,
                )
                embed.set_footer(text="v1.0 | Made by Beelzebub2")
                await message.channel.send(embed=embed)
        elif message.content.lower() == "clear":
            messages_to_remove = 1000
            user = await bot.fetch_user(int(message.author.id))
            async for message in user.history(limit=messages_to_remove):
                if message.author.id == bot.user.id:
                    await message.delete()
                    await asyncio.sleep(1)

            # Create and send an embed message
            embed = discord.Embed(
                title="Conversation Cleared",
                description="All messages have been cleared.",
                color=65280,
            )
            embed.set_footer(text="v1.0 | Made by Beelzebub2")
            await message.channel.send(embed=embed)
        else:
            # Handle other commands or conversations in DMs
            # Create and send an embed message
            embed = discord.Embed(
                title="Unknown Command",
                description="I'm sorry, I didn't understand that command.",
                color=16759808,
            )
            embed.set_footer(text="v1.0 | Made by Beelzebub2")
            await message.channel.send(embed=embed)


if __name__ == "__main__":
    init()
    bot.run(TOKEN)
