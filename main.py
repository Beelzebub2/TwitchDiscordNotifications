import asyncio
import datetime
import pickle
import io
import math
import signal
import shutil
import sys
import time
import os
import aiohttp
import requests
from PIL import Image, ImageDraw, ImageFont
import re
import discord
import traceback
from colorama import init, Fore, Style
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import concurrent.futures
from functions.configHandler import ConfigHandler
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
                                    embed.add_field(name="Viewers", value=viewers)
                                user_response = requests.get(user_url, headers=HEADERS)
                                user_data = user_response.json()
                                profile_picture_url = user_data["data"][0][
                                    "profile_image_url"
                                ]
                                profile_picture_url = profile_picture_url.replace(
                                    "{width}", "300"
                                ).replace("{height}", "300")
                                start_time_str = functions.others.generate_timestamp_string(started_at)
                                embed.add_field(name="Stream Title", value=title)
                                embed.set_thumbnail(url=profile_picture_url)
                                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
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
            timestamp=datetime.datetime.now()
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
                    print(" " * console_width, end="\r")
                    functions.others.log_print(
                        f"{functions.others.get_timestamp()} No data found for streamer: {streamer_name}"
                    )

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
                print(" " * console_width, end="\r")
                functions.others.log_print(
                    "\033[K"
                    + Fore.CYAN
                    + functions.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTYELLOW_EX
                    + ctx.author.name
                    + Fore.RESET
                    + f" requested their streamers: {len(streamer_list)}"
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

                num_pfps = len(pfps)
                max_images_per_row = 5
                image_width = 100
                image_height = 100
                num_rows = math.ceil(num_pfps / max_images_per_row)

                name_box_width = image_width
                name_box_height = 20
                name_box_color = (0, 0, 0)
                name_text_color = (255, 255, 255)
                font_size = 9
                font = ImageFont.truetype("arialbd.ttf", font_size)

                if num_pfps <= max_images_per_row:
                    combined_image_width = num_pfps * image_width
                else:
                    combined_image_width = max_images_per_row * image_width

                combined_image_height = num_rows * (image_height + name_box_height)

                combined_image = Image.new(
                    "RGB", (combined_image_width, combined_image_height)
                )

                x_offset = 0
                y_offset = name_box_height

                for i, (pfp_url, name) in enumerate(zip(pfps, names)):
                    pfp_response = requests.get(pfp_url)
                    pfp_image = Image.open(io.BytesIO(pfp_response.content))
                    pfp_image.thumbnail((image_width, image_height))

                    name_x = x_offset
                    name_y = y_offset - name_box_height

                    combined_image.paste(pfp_image, (x_offset, y_offset))

                    name_box = Image.new(
                        "RGB", (name_box_width, name_box_height), name_box_color
                    )

                    draw = ImageDraw.Draw(name_box)
                    text_bbox = draw.textbbox((0, 0), name, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_x = (name_box_width - text_width) // 2
                    text_y = (name_box_height - text_height) // 2
                    draw.text((text_x, text_y), name, fill=name_text_color, font=font)

                    combined_image.paste(name_box, (name_x, name_y))

                    x_offset += image_width

                    if x_offset >= combined_image_width:
                        x_offset = 0
                        y_offset += image_height + name_box_height

                combined_image.save("combined_image.png")

                embed = discord.Embed(
                    title=f"Your Streamers {member.name}",
                    description=f"**You are currently watching the following streamers:**",
                    color=10242047,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                embed.set_image(url="attachment://combined_image.png")

                with open("combined_image.png", "rb") as img_file:
                    file = discord.File(img_file)
                    await ctx.channel.send(file=file, embed=embed)
                os.remove("combined_image.png")

                return streamer_names, combined_image

            else:
                print(" " * console_width, end="\r")
                functions.others.log_print(
                    Fore.CYAN
                    + functions.others.get_timestamp()
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
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.channel.send(embed=embed)
        else:
            print(" " * console_width, end="\r")
            functions.others.log_print(
                Fore.CYAN
                + functions.others.get_timestamp()
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
                timestamp=datetime.datetime.now()
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
            timestamp=datetime.datetime.now()
        )
        

        sorted_commands = sorted(bot.commands, key=lambda x: x.name)

        for command in sorted_commands:
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


    @bot.event
    async def on_ready():
        ch.save_time(str(datetime.datetime.now()))
        if not ch.check_restart_status():
            bot_owner_id = ch.get_bot_owner_id()
            if not bot_owner_id:
                bot_info = await bot.application_info()
                owner = bot.get_user(int(bot_info.owner.id))
                ch.save_bot_owner_id(str(owner.id))
            else:
                owner = bot.get_user(int(bot_owner_id))
            embed = discord.Embed(
                title="Initialization Successful",
                description="Bot started successfully.",
                color=0x00FF00,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
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


async def get_custom_prefix(bot, message):
    if message.guild:
        guild_id = message.guild.id
        custom_prefix = ch.get_guild_prefix(guild_id)
        if custom_prefix:
            return custom_prefix
    return ch.get_prefix()


def custom_interrupt_handler(signum, frame):
    print(" " * console_width, end="\r")
    if len(processed_streamers) > 0:
        print(
            f"{Fore.LIGHTYELLOW_EX}[{Fore.RESET + Fore.LIGHTGREEN_EX}KeyboardInterrupt{Fore.LIGHTYELLOW_EX}]{Fore.RESET}{Fore.LIGHTWHITE_EX} Saving currently streaming streamers and exiting..."
        )
        data = {"Restarted": True, "Streamers": processed_streamers}
        ch.save_to_temp_json(data)
        os._exit(0)

    print(
        f"{Fore.LIGHTYELLOW_EX}[{Fore.RESET + Fore.LIGHTGREEN_EX}KeyboardInterrupt{Fore.LIGHTYELLOW_EX}]{Fore.RESET}{Fore.LIGHTWHITE_EX} No streamers currently streaming. exiting..."
    )
    os._exit(0)

async def load_extension(filename):
    try:
        await bot.load_extension(f'commands.{filename[:-3]}')
        return f"Loaded {filename}"
    except Exception as e:
        return f"Failed to load {filename}: {e}"

async def load_extensions():
    extension_files = [filename for filename in os.listdir('./commands') if filename.endswith('.py')]
    workers = len(extension_files) + 1
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = await asyncio.gather(*[load_extension(filename) for filename in extension_files])

    end_time = time.time()
    elapsed_time = end_time - start_time
    for result in results:
        print(result)
    print(f"Elapsed time: {elapsed_time:.4f} seconds")




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
    signal.signal(signal.SIGINT, custom_interrupt_handler)
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
        "ch": ch,
        "console_width": console_width,
        "processed_streamers": processed_streamers,
        "version": VERSION,
        "authorization": AUTHORIZATION,
        "client_id": CLIENT_ID,
        "date_format": date_format,
        "intents": intents
    }

    with open("variables.pkl", "wb") as file:
        pickle.dump(shared_variables, file)

    init()
    main()
    asyncio.run(loadAndStart())