import discord
import datetime
import aiohttp
import asyncio
import os
import pickle
import shutil
import time
import signal
from discord.ext import commands
from discord import Intents
from colorama import Fore
import requests
from functions.Sql_handler import SQLiteHandler
import functions.others
import concurrent.futures


class TwitchDiscordBot:
    def __init__(self):
        self.CLIENT_ID = os.environ.get("client_id")
        self.AUTHORIZATION = os.environ.get("authorization")
        self.TOKEN = os.environ.get("token")
        self.repo_url = "https://github.com/Beelzebub2/TwitchDiscordNotifications"
        self.VERSION = "v" + functions.others.get_version(self.repo_url)
        self.create_env()
        self.ch = SQLiteHandler("data.db")
        self.ch.set_prefix(",")
        self.ch.set_version(self.VERSION)
        intents = Intents.all()
        intents.dm_messages = True
        self.Loaded_commands = []
        self.Failed_commands = []
        self.bot = commands.Bot(
            command_prefix=commands.when_mentioned_or(self.ch.get_prefix()), intents=intents
        )
        self.bot.add_listener(self.on_ready)
        try:
            self.console_width = shutil.get_terminal_size().columns
        except AttributeError:
            self.console_width = 80
        self.bot.command_prefix = self.get_custom_prefix
        self.bot.remove_command("help")  # delete default help command
        if self.ch.check_restart_status():
            self.processed_streamers = self.ch.processed_streamers
        else:
            self.processed_streamers = []
        self.API_BASE_URL = "https://api.twitch.tv/helix/streams"
        self.HEADERS = {
            "Client-ID": self.CLIENT_ID,
            "Authorization": f"Bearer {self.AUTHORIZATION}",
        }
        self.date_format = "%Y-%m-%d %H:%M:%S.%f"
        self.shared_variables = {
            "console_width": self.console_width,
            "processed_streamers": self.processed_streamers,
            "version": self.VERSION,
            "authorization": self.AUTHORIZATION,
            "client_id": self.CLIENT_ID,
            "date_format": self.date_format,
            "loaded_commands": self.Loaded_commands,
            "failed_commands": self.Failed_commands,
            "intents": intents,
            "headers": self.HEADERS
        }
        with open("variables.pkl", "wb") as file:
            pickle.dump(self.shared_variables, file)

    async def check_stream(self, session, streamer_name):
        if not streamer_name:
            return False

        params = {
            "user_login": streamer_name,
        }

        async with session.get(
            self.API_BASE_URL, headers=self.HEADERS, params=params
        ) as response:
            if response.status == 200:
                data = await response.json()

                if "data" in data and len(data["data"]) > 0:
                    if streamer_name.lower() not in self.processed_streamers:
                        asyncio.create_task(
                            self.send_notification(streamer_name.strip(), data)
                        )
                        self.processed_streamers.append(streamer_name.lower())
                    return True
                if streamer_name.lower() in self.processed_streamers:
                    self.processed_streamers.remove(streamer_name.lower())

            return False

    async def send_notification(self, streamer_name, data):
        streamer_lists = self.ch.get_user_ids_with_streamers()
        for user_id, streamers in streamer_lists.items():
            try:
                member = self.bot.get_user(int(user_id))
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
                                    user_url, headers=self.HEADERS)
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
                                    text=f"{self.VERSION} | Made by Beelzebub2")
                                mention = f"||{member.mention}||"
                                embed.add_field(
                                    name="Stream Start Time (local)",
                                    value=start_time_str,
                                )
                                try:
                                    await dm_channel.send(mention, embed=embed)
                                    print(" " * self.console_width, end="\r")
                                    functions.others.log_print(
                                        Fore.CYAN
                                        + functions.others.get_timestamp()
                                        + Fore.RESET
                                        + " "
                                        + Fore.LIGHTGREEN_EX
                                        + f"Notification sent successfully for {Fore.CYAN + streamer_name + Fore.RESET}. {Fore.LIGHTGREEN_EX}to member {Fore.LIGHTCYAN_EX + member.name + Fore.RESET}"
                                    )
                                except discord.errors.Forbidden:
                                    print(" " * self.console_width, end="\r")
                                    functions.others.log_print(
                                        Fore.CYAN
                                        + functions.others.get_timestamp()
                                        + Fore.RESET
                                        + " "
                                        + f"Cannot send a message to user {member.name}. Missing permissions or DMs disabled."
                                    )
                            else:
                                print(" " * self.console_width, end="\r")
                                functions.others.log_print(
                                    Fore.CYAN
                                    + functions.others.get_timestamp()
                                    + Fore.RESET
                                    + " "
                                    + f"{streamer_name} is not streaming."
                                )
                                self.processed_streamers.remove(streamer_name)
            except discord.errors.NotFound:
                print(" " * self.console_width, end="\r")
                functions.others.log_print(
                    Fore.CYAN
                    + functions.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.RED
                    + f"User with ID {user_id} not found."
                    + Fore.RESET
                )

    async def on_ready(self):
        print("sTUCK ERHAPS?")
        self.ch.save_time(str(datetime.datetime.now()))
        if not self.ch.check_restart_status():
            bot_owner_id = self.ch.get_bot_owner_id()
            if not bot_owner_id:
                bot_info = await self.bot.application_info()
                owner_id = str(bot_info.owner.id)
                self.ch.save_bot_owner_id(owner_id)
                owner = self.bot.get_user(int(owner_id))
            else:
                owner = self.bot.get_user(int(bot_owner_id))
            bot_guilds = self.bot.guilds
            owner_in_guild = any(
                owner in guild.members for guild in bot_guilds)
            embed = discord.Embed(
                title="Initialization Successful",
                description="Bot started successfully.",
                color=0x00FF00,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
            embed.add_field(name="Loaded commands", value=len(self.Loaded_commands))
            embed.add_field(name="Failed commands",
                            value="\n".join(self.Failed_commands))
            if not owner_in_guild:
                functions.others.log_print(
                    f"{functions.others.get_timestamp()}{Fore.RED} [ERROR] Warning: Owner is not in any guild where the bot is present.")
            else:
                await owner.send(embed=embed)
        functions.others.clear_console()
        functions.others.set_console_title("TwitchDiscordNotifications")
        print(" " * self.console_width, end="\r")
        functions.others.log_print(
            Fore.CYAN
            + functions.others.get_timestamp()
            + Fore.RESET
            + Fore.LIGHTGREEN_EX
            + f" Running as {Fore.LIGHTCYAN_EX + self.bot.user.name + Fore.RESET}"
        )
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="Mention me to see my prefix"
        )
        await self.bot.change_presence(activity=activity)

        while True:
            start_time = time.time()
            print(" " * self.console_width, end="\r")
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

            streamers = self.ch.get_all_streamers()
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(
                    *[self.check_stream(session, streamer) for streamer in streamers]
                )

            end_time = time.time()
            elapsed_time = end_time - start_time

            if len(self.processed_streamers) != 0:
                print(" " * self.console_width, end="\r")
                print(
                    Fore.CYAN
                    + functions.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTGREEN_EX
                    + f"Currently streaming (Time taken: {elapsed_time:.2f} seconds): "
                    + Fore.RESET
                    + Fore.LIGHTWHITE_EX
                    + str(self.processed_streamers)
                    + Fore.RESET,
                    end="\r",
                )
            else:
                print(" " * self.console_width, end="\r")
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

    def create_env(self):
        if os.path.exists(".env"):
            return
        if self.CLIENT_ID and self.AUTHORIZATION and self.TOKEN:
            return

        if "REPLIT_DB_URL" in os.environ:
            if not self.CLIENT_ID or not self.AUTHORIZATION or not self.TOKEN:
                print("Running on Replit")

        if "DYNO" in os.environ:
            if not self.CLIENT_ID or not self.AUTHORIZATION or not self.TOKEN:
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

    async def load_extension(self, filename):
        try:
            await self.bot.load_extension(f'commands.{filename[:-3]}')
            return f"Loaded {filename}"
        except Exception as e:
            return f"Failed to load {filename}: {e}"

    async def load_extensions(self):
        extension_files = [filename for filename in os.listdir(
            './commands') if filename.endswith('.py')]
        workers = len(extension_files) + 1
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            results = await asyncio.gather(*[self.load_extension(filename) for filename in extension_files])

        end_time = time.time()
        elapsed_time = end_time - start_time
        for result in results:
            print(result)
            parts = result.split(" ")
            if len(parts) >= 2 and parts[0] == "Loaded":
                self.Loaded_commands.append(result)
            else:
                result = result.split(":")
                self.Failed_commands.append(result[0])

        print(f"Elapsed time: {elapsed_time:.4f} seconds")

    async def get_custom_prefix(self, bot, message):
        if message.guild:
            guild_id = message.guild.id
            custom_prefix = self.ch.get_guild_prefix(guild_id)
            if custom_prefix:
                return custom_prefix
        return self.ch.get_prefix()

    async def load_and_start(self):
        async with self.bot:
            try:
                await self.load_extensions()
                await self.bot.start(self.TOKEN)
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
    bot_instance = TwitchDiscordBot()
    signal.signal(signal.SIGINT, functions.others.custom_interrupt_handler)
    asyncio.run(bot_instance.load_and_start())
