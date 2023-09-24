import asyncio
import datetime
import io
import json
import aiohttp
import requests
import time
import os
from PIL import Image
import concurrent.futures
import re
import discord
import traceback
from colorama import init, Fore, Style
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv

load_dotenv()


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


class ConfigHandler:
    def __init__(self, config_file):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_config(self):
        with open(self.config_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_user(self, user_data):
        self.data = self.load_config()
        user_key = f"User{len(self.data['User-list']) + 1}"
        self.data["User-list"][user_key] = [user_data]
        self.save_config()
        return user_key

    def add_streamer_to_user(self, user_id, streamer):
        self.data = self.load_config()
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                if user_data["discord_id"] == user_id:
                    user_data["streamer_list"].append(streamer)
                    self.save_config()
                    return True
        return False

    def remove_streamer_from_user(self, discord_id, streamer):
        self.data = self.load_config()
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                if user_data["discord_id"] == discord_id:
                    if streamer in user_data["streamer_list"]:
                        user_data["streamer_list"].remove(streamer)
                        self.save_config()
                        return True
        return False

    def get_all_streamers(self):
        self.data = self.load_config()
        streamers = set()
        for user_data in self.data["User-list"].values():
            streamers.update(user_data[0]["streamer_list"])
        return list(streamers)

    def get_user_ids_with_streamers(self):
        self.data = self.load_config()
        user_ids_with_streamers = {}
        for user, user_data_list in self.data["User-list"].items():
            for user_data in user_data_list:
                user_id = user_data["discord_id"]
                streamer_list = user_data["streamer_list"]
                if user_id not in user_ids_with_streamers:
                    user_ids_with_streamers[user_id] = streamer_list
                else:
                    user_ids_with_streamers[user_id].extend(streamer_list)
        return user_ids_with_streamers

    def get_all_user_ids(self):
        self.data = self.load_config()
        user_ids = []
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                user_id = user_data["discord_id"]
                if user_id not in user_ids:
                    user_ids.append(user_id)
        return user_ids

    def get_streamers_for_user(self, user_id):
        self.data = self.load_config()
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                if user_data["discord_id"] == user_id:
                    return user_data["streamer_list"]
        return []

    def get_version(self):
        self.data = self.load_config()
        return self.data.get("Config", {}).get("version")

    def get_prefix(self):
        self.data = self.load_config()
        return self.data.get("Config", {}).get("prefix")

    def create_new_guild_template(self, guild_id, guild_name):
        self.data = self.load_config()
        self.data["Guilds"][str(guild_id)] = {
            "name": guild_name,
            "prefix": ",",
            "role_to_add": None,
        }
        self.save_config()

    def is_guild_in_config(self, guild_id):
        self.data = self.load_config()
        return str(guild_id) in self.data.get("Guilds", {})

    def get_guild_prefix(self, guild_id):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        return guild_info.get("prefix", "")

    def change_role_to_add(self, guild_id, new_role_id):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        guild_info["role_to_add"] = str(new_role_id)
        self.save_config()

    def get_role_to_add(self, guild_id):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        return guild_info.get("role_to_add", "")

    def change_guild_prefix(self, guild_id, new_prefix):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        guild_info["prefix"] = new_prefix
        self.save_config()


@error_handler
def main():
    @error_handler
    def get_timestamp():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def clear_console():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    @error_handler
    def generate_timestamp_string(started_at):
        started_datetime = datetime.datetime.fromisoformat(started_at.rstrip("Z"))
        unix_timestamp = int(started_datetime.timestamp()) + 3600
        timestamp_string = f"<t:{unix_timestamp}:T>"
        return timestamp_string

    @error_handler
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
                        asyncio.create_task(send_notification(streamer_name.strip()))
                        processed_streamers.append(streamer_name.lower())
                    return True

                if streamer_name in processed_streamers:
                    processed_streamers.remove(streamer_name)

            return False

    @error_handler
    async def send_notification(streamer_name):
        Data = ch.get_user_ids_with_streamers()

        for user_id, streamers in Data.items():
            try:
                member = await bot.fetch_user(int(user_id))
                if member:
                    dm_channel = member.dm_channel
                    if dm_channel is None:
                        dm_channel = await member.create_dm()
                    for streamer in streamers:
                        if streamer_name == streamer.strip():
                            url = f"https://api.twitch.tv/helix/streams?user_login={streamer_name}"
                            response = requests.get(url, headers=HEADERS)
                            data = response.json()
                            embed = discord.Embed(
                                title=f"{streamer_name} is streaming!",
                                description=f"Click [here](https://www.twitch.tv/{streamer_name}) to watch the stream.",
                                color=discord.Color.green(),
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
                                user_response = requests.get(user_url, headers=HEADERS)
                                user_data = user_response.json()
                                profile_picture_url = user_data["data"][0][
                                    "profile_image_url"
                                ]
                                profile_picture_url = profile_picture_url.replace(
                                    "{width}", "300"
                                ).replace("{height}", "300")
                                start_time_str = generate_timestamp_string(started_at)
                                embed.add_field(name="Stream Title", value=title)
                                embed.add_field(name="Viewers", value=viewers)
                                embed.set_thumbnail(url=profile_picture_url)
                                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                                mention = f"||{member.mention}||"
                                embed.add_field(
                                    name="Stream Start Time (local)",
                                    value=start_time_str,
                                )
                                try:
                                    await dm_channel.send(mention, embed=embed)
                                    print(
                                        Fore.CYAN
                                        + get_timestamp()
                                        + Fore.RESET
                                        + " "
                                        + Fore.LIGHTGREEN_EX
                                        + f"Notification sent successfully for {Fore.CYAN + streamer_name + Fore.RESET}."
                                    )
                                except discord.errors.Forbidden:
                                    print(
                                        Fore.CYAN
                                        + get_timestamp()
                                        + Fore.RESET
                                        + " "
                                        + f"Cannot send a message to user {member.name}. Missing permissions or DMs disabled."
                                    )
                            else:
                                print(
                                    Fore.CYAN
                                    + get_timestamp()
                                    + Fore.RESET
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

    @bot.command(
        name="watch",
        aliases=["w"],
        usage="watch <streamername_or_link>",
        help="Add a streamer to your watch list (provide either streamer name or link)",
    )
    async def watch(ctx, streamer_name_or_link: str):
        if "https://www.twitch.tv/" in streamer_name_or_link:
            streamer_name = re.search(
                r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
            ).group(1)
        else:
            streamer_name = streamer_name_or_link
        url = f"https://api.twitch.tv/helix/users?login={streamer_name}"
        headers = {
            "Client-ID": f"{CLIENT_ID}",
            "Authorization": f"Bearer {AUTHORIZATION}",
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data["data"]:
            print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"{Fore.CYAN + streamer_name + Fore.RESET} Twitch profile not found."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Streamer not found",
                description=f"**__{streamer_name}__** was not found.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
            await ctx.send(embed=embed)
            return
        pfp = data["data"][0]["profile_image_url"]
        user_id = str(ctx.author.id)
        user_ids = ch.get_all_user_ids()
        if user_id in user_ids:
            streamer_list = ch.get_streamers_for_user(user_id)
            if streamer_name.lower() not in [s.lower().strip() for s in streamer_list]:
                ch.add_streamer_to_user(user_id, streamer_name.strip())
                streamer_list.append(streamer_name.strip())
                print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTGREEN_EX
                    + f"Added {Fore.CYAN + streamer_name + Fore.RESET} to user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist."
                    + Fore.RESET
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description=f"Added **__{streamer_name}__** to your watchlist.",
                    color=65280,
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                embed.set_thumbnail(url=pfp)
                await ctx.send(embed=embed)
            else:
                print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + f"{Fore.CYAN + streamer_name + Fore.RESET} is already in user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist."
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description=f"{streamer_name} is already in your watchlist.",
                    color=16759808,
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.send(embed=embed)
        else:
            ch.add_user(
                user_data={
                    "discord_username": ctx.author.name,
                    "discord_id": user_id,
                    "streamer_list": [streamer_name.strip()],
                }
            )
            print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.LIGHTGREEN_EX
                + f"Created a new watchlist for user {Fore.CYAN + ctx.author.name + Fore.RESET} and added {Fore.CYAN + streamer_name + Fore.RESET}."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Stream Watchlist",
                description=f"Created a new watchlist for you and added {streamer_name}.",
                color=65280,
            )
            embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
            await ctx.send(embed=embed)

    @bot.command(
        name="unwatch",
        aliases=["u"],
        usage="unwatch <streamername_or_link>",
        help="Removes the streamer from your watch list (provide either streamer name or link)",
    )
    async def unwatch(ctx, streamer_name_or_link: str):
        if "https://www.twitch.tv/" in streamer_name_or_link:
            streamer_name = re.search(
                r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
            ).group(1)
        else:
            streamer_name = streamer_name_or_link

        user_id = str(ctx.author.id)
        user_ids = ch.get_all_user_ids()
        if user_id in user_ids:
            streamer_list = ch.get_streamers_for_user(user_id)
            if any(streamer_name.lower() == s.lower() for s in streamer_list):
                ch.remove_streamer_from_user(user_id, streamer_name)
                if (
                    streamer_name in processed_streamers
                    and streamer_name not in ch.get_all_streamers()
                ):
                    processed_streamers.remove(streamer_name)

                print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTGREEN_EX
                    + f"Removed {Fore.CYAN + streamer_name + Fore.RESET} from user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist."
                    + Fore.RESET
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description=f"Removed {streamer_name} from your watchlist.",
                    color=65280,
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.channel.send(embed=embed)
            else:
                print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + f"{Fore.CYAN + streamer_name + Fore.RESET} is not in user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist."
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description=f"{streamer_name} is not in your watchlist.",
                    color=16759808,
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.channel.send(embed=embed)

    @bot.command(
        name="clear",
        aliases=["c"],
        help="Clears all the messages sent by the bot",
        usage="clear",
    )
    async def clear_bot_messages(ctx):
        messages_to_remove = 1000
        user = await bot.fetch_user(ctx.author.id)

        async for message in ctx.history(limit=messages_to_remove):
            if message.author.id == bot.user.id:
                await message.delete()
                await asyncio.sleep(1)

        # Create and send an embed message
        embed = discord.Embed(
            title="Conversation Cleared",
            description="All messages have been cleared.",
            color=65280,
        )
        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
        await ctx.send(embed=embed)

    async def fetch_streamer_data(session, streamer_name, pfps, names):
        streamer_name = streamer_name.replace(" ", "")
        url = f"https://api.twitch.tv/helix/users?login={streamer_name}"

        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    streamer_data = data["data"][0]
                    profile_picture_url = streamer_data.get("profile_image_url", "")
                    profile_picture_url = profile_picture_url.replace(
                        "{width}", "150"
                    ).replace("{height}", "150")
                    pfps.append(profile_picture_url)
                    names.append(streamer_data["display_name"])
                else:
                    print(f"No data found for streamer: {streamer_name}")

    @bot.command(
        name="list",
        aliases=["l"],
        help="Returns an embed with a list of all the streamers you're currently watching",
        usage="list",
    )
    async def list_streamers(ctx):
        user_id = str(ctx.author.id)
        member = await bot.fetch_user(int(user_id))
        user_ids = ch.get_all_user_ids()
        if user_id in user_ids:
            streamer_list = ch.get_streamers_for_user(user_id)
            if streamer_list:
                streamer_names = ", ".join(streamer_list)
                print(
                    "\033[K"
                    + Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTYELLOW_EX
                    + ctx.author.name
                    + Fore.RESET
                    + f" requested their streamers: {streamer_names}"
                )

                pfps = []
                names = []

                async with aiohttp.ClientSession() as session:
                    await asyncio.gather(
                        *[
                            fetch_streamer_data(session, streamer, pfps, names)
                            for streamer in streamer_list
                        ]
                    )

                pfp_size = (100, 100)
                image_width = pfp_size[0] * len(pfps)
                combined_image = Image.new("RGB", (image_width, pfp_size[1]))
                x_offset = 0
                for pfp_url in pfps:
                    pfp_response = requests.get(pfp_url)
                    pfp_image = Image.open(io.BytesIO(pfp_response.content))
                    pfp_image = pfp_image.resize(pfp_size)
                    y_offset = (combined_image.height - pfp_size[1]) // 2
                    combined_image.paste(pfp_image, (x_offset, y_offset))
                    x_offset += pfp_size[0]
                combined_image.save("combined_image.png")

                embed = discord.Embed(
                    title=f"Your Streamers {member.name}",
                    description=f"**You are currently watching the following streamers:\n{streamer_names}**",
                    color=10242047,
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                embed.set_image(url="attachment://combined_image.png")

                with open("combined_image.png", "rb") as img_file:
                    file = discord.File(img_file)
                    await ctx.channel.send(file=file, embed=embed)
                os.remove("combined_image.png")

            else:
                print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.YELLOW
                    + f"{Fore.CYAN + ctx.author.name + Fore.RESET} requested their streamers, but the watchlist is empty."
                    + Fore.RESET
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description="Your watchlist is empty.",
                    color=16759808,
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.channel.send(embed=embed)
        else:
            print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"{Fore.CYAN + ctx.author.name + Fore.RESET} requested their streamers, but they don't have a watchlist yet."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Stream Watchlist",
                description="You don't have a watchlist yet.",
                color=16711680,
            )
            embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
            await ctx.channel.send(embed=embed)

    @bot.command(
        name="help",
        aliases=["h", "commands", "command"],
        usage="help",
        help="Shows all the available commands and their descriptions",
    )
    async def list_commands(ctx):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are the available commands, their descriptions, and usage:",
            color=65280,
        )

        for command in bot.commands:
            if command.hidden:
                continue

            description = command.help or "No description available."
            aliases = ", ".join(command.aliases) if command.aliases else "No aliases"
            usage = command.usage or f"No usage specified for {command.name}"

            embed.add_field(
                name=f"**{command.name.capitalize()}**",
                value=f"Description: {description}\nUsage: `{usage}`\nAliases: {aliases}",
                inline=False,
            )

        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")

        await ctx.send(embed=embed)

    @bot.command(
        name="invite",
        aliases=["i"],
        help="Generates bot invite link",
        usage="invite",
    )
    async def invite(ctx):
        # Create an embed to display the commands and their descriptions
        embed = discord.Embed(
            title="Invite Me!",
            description=f"[Click here](https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot)",
            color=65280,
        )
        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")

        await ctx.send(embed=embed)

    @bot.command(
        name="configrole",
        aliases=["cr"],
        usage="configrole <@role>",
        help="Change the role to add in the server configuration",
    )
    async def prefix_config_role(ctx, role: discord.Role):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(
                "You do not have the necessary permissions to use this command."
            )
            return
        guild_id = ctx.guild.id
        role_id = role.id
        ch.change_role_to_add(guild_id, role_id)
        await ctx.send(
            f"The role to add has been updated to {role.mention} in the server configuration."
        )

    @bot.command(
        name="configprefix",
        aliases=["cx"],
        usage="configprefix <new_prefix>",
        help="changes the default prefix of the guild",
    )
    async def change_guild_prefix(ctx, new_prefix: str):
        if ctx.author.guild_permissions.administrator:
            guild_id = ctx.guild.id
            ch.change_guild_prefix(guild_id, new_prefix)
            await ctx.send(f"Prefix for this guild has been updated to `{new_prefix}`.")
        else:
            await ctx.send(
                "You do not have the necessary permissions to change the prefix."
            )

    @bot.event
    async def on_disconnect():
        clear_console()

    @bot.event
    async def on_resumed():
        print(
            Fore.CYAN
            + get_timestamp()
            + Fore.RESET
            + Fore.LIGHTGREEN_EX
            + f" Running as {Fore.LIGHTCYAN_EX + bot.user.name + Fore.RESET}"
        )
        clear_console()

    @bot.event
    async def on_ready():
        clear_console()
        print(
            Fore.CYAN
            + get_timestamp()
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

            print(
                "\033[K"
                + Fore.CYAN
                + get_timestamp()
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
                print(
                    Fore.CYAN
                    + get_timestamp()
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
                print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + Fore.LIGHTWHITE_EX
                    + f" Checked {len(streamers)} streamers. Time taken: {elapsed_time:.2f} seconds"
                    + Fore.RESET,
                    end="\r",
                )

            await asyncio.sleep(5)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            command = ctx.message.content
            print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"Command {Fore.CYAN + command + Fore.RESET} doesn't exist."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Command not found",
                description=f"Command **__{command}__** does not exist use .help for more info.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
            await ctx.send(embed=embed)
        else:
            # Handle other errors
            await ctx.send(f"An error occurred: {error}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if message.guild:
            guild_id = message.guild.id
            guild_name = message.guild.name
            if not ch.is_guild_in_config(guild_id):
                ch.create_new_guild_template(guild_id, guild_name)

        if bot.user.mentioned_in(message):
            if isinstance(message.channel, discord.DMChannel):
                embed = discord.Embed(
                    title=f"Hello, {message.author.display_name}!",
                    description=f"My prefix is: `{ch.get_prefix()}`",
                    color=discord.Color.green(),
                )

            elif isinstance(message.channel, discord.TextChannel):
                guild_prefix = bot.command_prefix
                if message.guild:
                    guild_prefix = ch.get_guild_prefix(message.guild.id)

                embed = discord.Embed(
                    title=f"Hello, {message.author.display_name}!",
                    description=f"My prefix for this server is: `{guild_prefix}`",
                    color=discord.Color.green(),
                )
            await message.channel.send(embed=embed)

        await bot.process_commands(message)

    @bot.event
    async def on_member_join(member):
        guild_id = member.guild.id

        role_id = int(ch.get_role_to_add(guild_id))
        general_channel = member.guild.text_channels[0]

        if not role_id:
            await general_channel.send(
                f"Welcome {member.mention} to the server, but it seems the server administrator has not configured the role assignment. Please contact an admin for assistance."
            )
        else:
            role = member.guild.get_role(role_id)
            if role:
                if role not in member.roles:
                    await member.add_roles(role)
                    print(
                        f"Assigned role named {role.name} to {member.display_name} in the target guild."
                    )
            else:
                await general_channel.send(
                    f"Welcome {member.mention} to the server, but the configured role with ID {role_id} does not exist. Please contact an admin to update the role ID."
                )


@error_handler
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
        "client_id": "Your client id",
        "authorization": "Your authorization token",
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


async def get_custom_prefix(bot, message):
    if message.guild:
        guild_id = message.guild.id
        custom_prefix = ch.get_guild_prefix(guild_id)
        if custom_prefix:
            return custom_prefix
    return ch.get_prefix()


if __name__ == "__main__":
    CLIENT_ID = os.environ.get("client_id")
    AUTHORIZATION = os.environ.get("authorization")
    TOKEN = os.environ.get("token")
    create_env()
    ch = ConfigHandler("data.json")
    intents = Intents.all()
    intents.dm_messages = True
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(ch.get_prefix), intents=intents
    )
    bot.command_prefix = get_custom_prefix
    bot.remove_command("help")  # delete default help command
    processed_streamers = []
    API_BASE_URL = "https://api.twitch.tv/helix/streams"
    VERSION = ch.get_version()
    HEADERS = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {AUTHORIZATION}",
    }
    init()
    main()
    bot.run(TOKEN)
