import sys
import tempfile
import discord
import datetime
import aiohttp
import asyncio
import os
import shutil
import time
import signal
from discord.ext import commands
from discord import Intents
from colorama import Fore
import dotenv
import requests
from Functions.Sql_handler import SQLiteHandler
from Functions import Json_config_hanldler
import Functions.others
import concurrent.futures
import Utilities.updater
import Utilities.custom_decorators


class TwitchDiscordBot:
    def __init__(self):
        signal.signal(signal.SIGINT, self.custom_interrupt_handler)
        self.CLIENT_ID = os.environ.get("client_id")
        self.CLIENT_SECRET = os.environ.get("client_secret")
        self.AUTHORIZATION = os.environ.get("authorization")
        self.TOKEN = os.environ.get("token")
        self.others = Functions.others
        self.cwd = os.getcwd()
        self.ch = SQLiteHandler()
        self.chj = Json_config_hanldler.JsonConfigHandler(
            os.path.join(self.cwd, "UI\\config.json")
        )
        self.autoupdate = self.chj.get_autoupdates()
        self.VERSION = self.chj.get_version()
        self.chj.set_pid(self.others.get_current_pid())
        self.create_env()
        self.ch.set_prefix(self.chj.get_prefix())
        self.ch.set_version(self.VERSION)
        intents = Intents.all()
        intents.dm_messages = True
        self.Loaded_commands = []
        self.Failed_commands = []
        self.streamer_data_cache = {}
        self.bot = commands.Bot(
            command_prefix=commands.when_mentioned_or(self.ch.get_prefix()),
            intents=intents,
            case_insensitive=True,

        )
        self.temp_dir = tempfile.gettempdir()
        self.heartbeat_file_path = os.path.join(
            self.temp_dir, "TwitchDiscordNotifications\\heartbeat.txt"
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
            "headers": self.HEADERS,
            "streamers_cache": self.streamer_data_cache,
        }
        self.others.pickle_variable(self.shared_variables)

    async def check_stream(self, session, streamer_name):
        if not streamer_name:
            return False

        streamer_name = streamer_name.lower()

        params = {
            "user_login": streamer_name,
        }

        async with session.get(
            self.API_BASE_URL, headers=self.HEADERS, params=params
        ) as response:
            if response.status == 200:
                data = await response.json()

                if "data" in data and data["data"]:
                    if streamer_name not in self.processed_streamers:
                        asyncio.create_task(
                            self.send_notification(streamer_name.strip(), data)
                        )
                        self.processed_streamers.append(streamer_name)
                    return True
                if streamer_name in self.processed_streamers:
                    self.processed_streamers.remove(streamer_name)
            elif response.status == 401:
                self.get_twitch_access_token(
                    self.CLIENT_ID, self.CLIENT_SECRET)

            return False

    def get_twitch_access_token(self, client_id, client_secret):
        oauth_url = "https://id.twitch.tv/oauth2/token"

        params = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "user:read:email",
        }

        try:
            response = requests.post(oauth_url, params=params)
            response_data = response.json()

            if "access_token" in response_data:
                access_token = response_data["access_token"]
                self.AUTHORIZATION = access_token

                os.environ["authorization"] = access_token
                dotenv.set_key(env_file, "authorization", access_token)

                self.others.log_print(
                    self.others.get_timestamp()
                    + self.others.holders(1)
                    + f"Authorization token invalid. Generated new authorization token. Restarting Bot{Fore.RESET}"
                )

                python = sys.executable
                os.execl(python, python, *sys.argv)
            else:
                self.others.log_print(
                    self.others.holders(2)
                    + "Failed to obtain an access token from Twitch."
                )
        except Exception as e:
            self.others.log_print(
                self.others.holders(2)
                + "An error occurred while obtaining the access token:",
                str(e),
            )

    @Utilities.custom_decorators.performance_tracker
    async def send_notification(self, streamer_name, data):
        for user_id, streamers in self.ids_with_streamers:
            try:
                member = self.bot.get_user(int(user_id))
                if not member:
                    continue

                dm_channel = member.dm_channel or await member.create_dm()

                for streamer in streamers:
                    if streamer_name == streamer.strip():
                        if "data" not in data or not data["data"]:
                            self.others.log_print(
                                f"{self.others.get_timestamp()}{self.others.holders(2)}{streamer_name} is no longer streaming."
                            )
                            self.processed_streamers.remove(streamer_name)
                            continue

                        stream_data = data["data"][0]
                        started_at = stream_data.get("started_at")
                        user_id = stream_data.get("user_id")

                        if not started_at or not user_id:
                            continue

                        user_url = f"https://api.twitch.tv/helix/users?id={user_id}"
                        user_response = requests.get(
                            user_url, headers=self.HEADERS)
                        user_data = user_response.json()
                        profile_picture_url = user_data["data"][0].get(
                            "profile_image_url"
                        )

                        if profile_picture_url:
                            profile_picture_url = profile_picture_url.replace(
                                "{width}", "300"
                            ).replace("{height}", "300")

                        start_time_str = self.others.generate_timestamp_string(
                            started_at
                        )
                        title = stream_data.get("title", "")
                        viewers = stream_data.get("viewer_count", 0)

                        embed = discord.Embed(
                            title=f"{streamer_name} is streaming!",
                            description=f"Click [here](https://www.twitch.tv/{streamer_name}) to watch the stream.",
                            color=discord.Color.green(),
                            timestamp=datetime.datetime.now(),
                        )

                        if stream_data.get("game_name"):
                            embed.add_field(
                                name="Game", value=stream_data["game_name"])

                        embed.add_field(
                            name="Viewers",
                            value="No viewers. Be the first!"
                            if viewers == 0
                            else viewers,
                        )
                        embed.add_field(name="Title", value=title)
                        embed.set_thumbnail(url=profile_picture_url)
                        embed.set_footer(
                            text=f"{self.VERSION} | Made by Beelzebub2")
                        mention = f"||{member.mention}||"
                        embed.add_field(
                            name="Stream Start Time (local)", value=start_time_str
                        )

                        max_retry_attempts = 3
                        for attempt in range(max_retry_attempts):
                            try:
                                await dm_channel.send(mention, embed=embed)
                                self.others.log_print(
                                    f"{self.others.get_timestamp()}"
                                    f"{self.others.holders(1)}Notification sent successfully for "
                                    f"{Fore.CYAN}{streamer_name}. {Fore.LIGHTGREEN_EX}to member "
                                    f"{Fore.LIGHTCYAN_EX + member.name + Fore.RESET}",
                                    show_message=False,
                                )
                                break
                            except discord.errors.DiscordServerError:
                                self.others.log_print(
                                    f"{self.others.get_timestamp()}"
                                    f"{self.others.holders(3)}Attempt {attempt + 1} - Discord server error",
                                    show_message=False)
                                if attempt == max_retry_attempts - 1:
                                    self.others.log_print(
                                        f"{self.others.get_timestamp()}"
                                        f"{self.others.holders(2)}Max retry attempts reached. Could not send notification.",
                                        show_message=False)
                                else:
                                    await asyncio.sleep(1)

                            except discord.errors.Forbidden:
                                self.others.log_print(
                                    f"{self.others.get_timestamp()}"
                                    f"{self.others.holders(2)}Cannot send a message to user {member.name}. "
                                    f"Missing permissions or DMs disabled.",
                                    show_message=False,
                                )
            except discord.errors.NotFound:
                self.others.log_print(
                    f"{self.others.get_timestamp()}{self.others.holders(2)}User with ID {user_id} not found.",
                    show_message=False,
                )
                continue

    async def on_ready(self):
        self.ch.save_time(str(datetime.datetime.now()))
        self.chj.set_time(str(datetime.datetime.now()))
        self.bot.loop.create_task(self.check_for_updates())
        self.bot.loop.create_task(self.cache_streamer_data())
        self.bot.loop.create_task(self.heart_beat())
        self.bot.loop.create_task(self.create_backup())
        if not self.ch.check_restart_status():
            bot_owner_id = self.ch.get_bot_owner_id()
            if not bot_owner_id:
                bot_info = await self.bot.application_info()
                owner_id = str(bot_info.owner.id)
                self.ch.save_bot_owner_id(owner_id)
                self.owner = self.bot.get_user(int(owner_id))
            else:
                self.owner = self.bot.get_user(int(bot_owner_id))

            bot_guilds = self.bot.guilds
            owner_in_guild = any(
                self.owner in guild.members for guild in bot_guilds)

            embed = discord.Embed(
                title="Initialization Successful",
                description="Bot started successfully.",
                color=0x00FF00,
                timestamp=datetime.datetime.now(),
            )

            embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
            embed.add_field(name="Loaded commands",
                            value=len(self.Loaded_commands))
            embed.add_field(name="Failed commands",
                            value=len(self.Failed_commands))

            if not owner_in_guild:
                self.others.log_print(
                    f"{self.others.get_timestamp()}{self.others.holders(2)}Warning: Owner is not in any guild where the bot is present."
                )
            else:
                await self.owner.send(embed=embed)

        self.others.clear_console()
        self.others.set_console_title("TwitchDiscordNotifications")

        self.others.log_print(
            f"{Fore.CYAN}{self.others.get_timestamp()}{Fore.RESET}{self.others.holders(3)}"
            f"{Fore.RESET}Running as {Fore.LIGHTCYAN_EX + self.bot.user.name + Fore.RESET} {Fore.LIGHTYELLOW_EX + self.VERSION + Fore.RESET}"
        )

        activity = discord.Activity(
            type=discord.ActivityType.watching, name="Mention me to see my prefix"
        )
        await self.bot.change_presence(activity=activity)
        self.bot.loop.create_task(self.check_streamers())

    @Utilities.custom_decorators.performance_tracker
    async def check_streamers(self):
        while True:
            start_time = time.perf_counter()

            print(
                "\033[K"
                + f"{Fore.CYAN}{self.others.get_timestamp()}{Fore.RESET}{self.others.holders(3)}{Fore.RESET}Checking",
                end="\r",
            )

            streamers = self.ch.get_all_streamers()
            self.ids_with_streamers = self.ch.get_user_ids_with_streamers().items()

            try:
                async with aiohttp.ClientSession() as session:
                    await asyncio.gather(
                        *[self.check_stream(session, streamer) for streamer in streamers]
                    )

            except aiohttp.ClientConnectorError:
                continue

            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            self.remove_old_streamers(streamers)

            if len(self.processed_streamers) != 0:
                print(
                    f"{Fore.CYAN}{self.others.get_timestamp()}{Fore.RESET}{Fore.LIGHTGREEN_EX}{self.others.holders(1)}"
                    f"Currently streaming {Fore.LIGHTWHITE_EX}{len(self.processed_streamers)}{Fore.RESET} "
                    f"{Fore.LIGHTGREEN_EX}Total: {Fore.LIGHTWHITE_EX}{len(streamers)}{Fore.LIGHTGREEN_EX} "
                    f"(Time taken: {elapsed_time:.2f} seconds){Fore.RESET}",
                    end="\r",
                )
            else:
                print(
                    f"{Fore.CYAN}{self.others.get_timestamp()}{Fore.RESET}{Fore.LIGHTGREEN_EX}{self.others.holders(1)}"
                    f"Checked {len(streamers)} streamers. Time taken: {elapsed_time:.2f} seconds",
                    end="\r",
                )

            await asyncio.sleep(5)

    @Utilities.custom_decorators.performance_tracker
    async def check_for_updates(self):
        while True:
            result = Utilities.updater.search_for_updates(self.autoupdate)
            if result:
                embed = discord.Embed(
                    title="Update Successful",
                    description="Bot Updated successfully.",
                    color=0x00FF00,
                    timestamp=datetime.datetime.now(),
                )
                change_log = self.others.get_changelog()
                embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
                embed.add_field(name="From", value=result[1])
                embed.add_field(name="To", value=result[2])
                embed.add_field(
                    name="Changelog", value=f"```diff\n{change_log}```", inline=False
                )
                await self.owner.send(embed=embed)
                self.others.pickle_variable(self.shared_variables)
                data = {"Restarted": True,
                        "Streamers": self.processed_streamers}
                self.ch.save_to_temp_json(data)
                python = sys.executable
                os.execl(python, python, *sys.argv)
            await asyncio.sleep(600)

    @Utilities.custom_decorators.performance_tracker
    async def heart_beat(self):
        while True:
            with open(self.heartbeat_file_path, "w") as heartbeat_file:
                heartbeat_file.write(str(time.time()))
            await asyncio.sleep(2)

    @Utilities.custom_decorators.performance_tracker
    async def create_backup(self):
        #TODO  only if backups are enabled
        while True:
            os.makedirs(backup_folder, exist_ok=True)
            self.db_folder = os.path.join(
                app_data_dir, "TwitchDiscordNotifications")
            self.default_db_file = os.path.join(self.db_folder, "data.db")

            current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
            backup_file_name = f"backup_{current_time}.db"
            backup_file_path = os.path.join(backup_folder, backup_file_name)

            if not os.path.exists(backup_file_path):
                shutil.copy(self.default_db_file, backup_file_path)
                self.others.log_print(
                    f"{self.others.get_timestamp()}{self.others.holders(1)}Created Backup file! {backup_file_name} saved in {self.db_folder}", show_message=False
                )

            backup_files = sorted(os.listdir(backup_folder), reverse=True)
            if len(backup_files) > 12:
                files_to_delete = backup_files[12:]
                for file in files_to_delete:
                    os.remove(os.path.join(backup_folder, file))
            await asyncio.sleep(3600)

    @Utilities.custom_decorators.performance_tracker
    async def cache_streamer_data(self):
        while True:
            streamer_list = self.ch.get_all_streamers()

            async with aiohttp.ClientSession() as session:
                await asyncio.gather(
                    *[
                        self.fetch_and_cache_streamer_data(session, streamer)
                        for streamer in streamer_list
                    ]
                )
            self.others.pickle_variable(self.shared_variables)
            await asyncio.sleep(60)

    @Utilities.custom_decorators.performance_tracker
    async def fetch_and_cache_streamer_data(self, session, streamer_name):
        streamer_name = streamer_name.replace(" ", "")
        url = f"https://api.twitch.tv/helix/users?login={streamer_name}"

        if streamer_name in self.streamer_data_cache:
            return

        async with session.get(url, headers=self.HEADERS) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    streamer_data = data["data"][0]
                    self.streamer_data_cache[streamer_name] = streamer_data

    def custom_interrupt_handler(self, signum, frame):
        if len(self.processed_streamers) > 0:
            self.others.log_print(
                f"{self.others.get_timestamp()} {Fore.LIGHTYELLOW_EX}[{Fore.RESET + Fore.LIGHTGREEN_EX}KeyboardInterrupt{Fore.LIGHTYELLOW_EX}]{Fore.RESET}{Fore.LIGHTWHITE_EX} Saving currently streaming streamers and exiting..."
            )
            data = {"Restarted": True, "Streamers": self.processed_streamers}
            self.ch.save_to_temp_json(data)
            os._exit(0)

        self.others.log_print(
            f"{self.others.get_timestamp()} {Fore.LIGHTYELLOW_EX}[{Fore.RESET + Fore.LIGHTGREEN_EX}KeyboardInterrupt{Fore.LIGHTYELLOW_EX}]{Fore.RESET}{Fore.LIGHTWHITE_EX} No streamers currently streaming. exiting..."
        )
        os._exit(0)

    @Utilities.custom_decorators.run_in_thread
    def remove_old_streamers(self, streamers):
        streamers_set = set(map(str.lower, streamers))
        processed_streamers_set = set(map(str.lower, self.processed_streamers))
        items_to_remove = processed_streamers_set - streamers_set
        self.processed_streamers = [
            s for s in self.processed_streamers if s.lower() not in items_to_remove
        ]

    # TODO fix replit .env directory from appdata to local cwd
    def create_env(self):
        if os.path.exists(".env"):
            return
        if self.CLIENT_ID and self.AUTHORIZATION and self.TOKEN and self.CLIENT_SECRET:
            return

        if "REPLIT_DB_URL" in os.environ:
            if (
                not self.CLIENT_ID
                or not self.AUTHORIZATION
                or not self.TOKEN
                or not self.CLIENT_SECRET
            ):
                print("Running on Replit")

        if "DYNO" in os.environ:
            if (
                not self.CLIENT_ID
                or not self.AUTHORIZATION
                or not self.TOKEN
                or not self.CLIENT_SECRET
            ):
                print("Running on Heroku")

        env_keys = {
            "client_id": "Your Twitch application client id",
            "client_secret": "Your Twitch application client secret",
            "authorization": "Your Twitch application authorization token",
            "token": "Your discord bot token",
        }

        app_data_dir = os.getenv("APPDATA")

        env_folder = os.path.join(app_data_dir, "TwitchDiscordNotifications")
        os.makedirs(env_folder, exist_ok=True)

        env_file_path = os.path.join(env_folder, ".env")

        with open(env_file_path, "w") as env_file:
            for key, value in env_keys.items():
                env_file.write(f"{key}={value}\n")

        if os.path.exists(env_file_path):
            print(
                f"Secrets missing! Created successfully. Please change filler text in .env on {env_folder} "
            )
            os._exit(0)

    async def load_extension(self, filename):
        try:
            start_time = time.perf_counter()
            await self.bot.load_extension(f"commands.{filename[:-3]}")
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            formatted_time = self.others.format_elapsed_time(elapsed_time)

            max_extension_width = max(
                len(filename[:-3]), self.max_extension_width)
            formatted_filename = f"{filename[:-3]:<{max_extension_width}}"
            formatted_in = "in"

            success_message = (
                f"{self.others.get_timestamp()}{Fore.LIGHTGREEN_EX}{self.others.holders(1)}Loaded "
                f"{Fore.LIGHTCYAN_EX}{formatted_filename} {formatted_in} {formatted_time:>2}"
            )
            return success_message, filename
        except Exception as e:
            error_message = (
                f"{self.others.get_timestamp()}{Fore.LIGHTRED_EX}{self.others.holders(2)}Failed to load "
                f"{Fore.LIGHTYELLOW_EX}{filename}{Fore.RESET}: {e}"
            )
            return error_message, filename

    async def load_extensions(self):
        extension_files = [
            filename
            for filename in os.listdir("./commands")
            if filename.endswith(".py")
        ]
        workers = len(extension_files) + 1
        start_time = time.perf_counter()

        self.max_extension_width = max(
            len(filename[:-3]) for filename in extension_files
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            results = await asyncio.gather(
                *[self.load_extension(filename) for filename in extension_files]
            )

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        formatted_total_time = self.others.format_elapsed_time(elapsed_time)

        for result, filename in results:
            print(result)
            parts = result.split() if not isinstance(result, tuple) else result
            if len(parts) >= 2 and parts[3] == "Loaded":
                self.Loaded_commands.append(result)
            else:
                self.others.log_print(
                    result, show_message=False, log_file_name="Failed Commands Log.txt")
                self.Failed_commands.append(filename[:-3])
        self.others.pickle_variable(self.shared_variables)

        print(
            f"{self.others.get_timestamp()} {Fore.LIGHTMAGENTA_EX}[PERFORMANCE] Elapsed time: "
            f"{Fore.LIGHTYELLOW_EX}{formatted_total_time}\n{Fore.LIGHTWHITE_EX}Logging in! ..."
        )

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
                self.others.clear_console()
                print(
                    Fore.LIGHTRED_EX
                    + {self.others.holders(2)}
                    + Fore.LIGHTYELLOW_EX
                    + f"Please grant all the intents to your bot on https://discord.com/developers/applications/{self.bot.user.id}/bot"
                    + Fore.RESET
                )
                os._exit(0)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    app_data_dir = os.getenv("APPDATA")
    backup_folder = os.path.join(
        app_data_dir, "TwitchDiscordNotifications\\TDNBackups")
    env_file = os.path.join(app_data_dir, "TwitchDiscordNotifications\\.env")
    dotenv.load_dotenv(env_file)
    bot_instance = TwitchDiscordBot()
    asyncio.run(bot_instance.load_and_start())
