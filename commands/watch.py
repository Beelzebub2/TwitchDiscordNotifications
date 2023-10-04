import datetime
from discord.ext import commands
import requests
from colorama import Fore
import discord
from functions.others import get_timestamp, log_print
import re
import pickle

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

ch = variables["ch"]
console_width = variables["console_width"]
processed_streamers = variables["processed_streamers"]
VERSION = variables["version"]
AUTHORIZATION = variables["authorization"]
CLIENT_ID = variables["client_id"]

class Watch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="watch",
        aliases=["w"],
        usage="watch <streamername_or_link>",
        help="Add a streamer to your watch list (provide either streamer name or link)",
    )
    async def watch(self, ctx, streamer_name_or_link: str):
        if "https://www.twitch.tv/" in streamer_name_or_link:
            streamer_name = re.search(
                r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
            ).group(1)
            streamer_name = streamer_name.lower()
        else:
            streamer_name = streamer_name_or_link.lower()
        url = f"https://api.twitch.tv/helix/users?login={streamer_name}"
        headers = {
            "Client-ID": f"{CLIENT_ID}",
            "Authorization": f"Bearer {AUTHORIZATION}",
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data["data"]:
            print(" " * console_width, end="\r")
            log_print(
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
                timestamp=datetime.datetime.now()
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
                print(" " * console_width, end="\r")
                log_print(
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
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                embed.set_thumbnail(url=pfp)
                await ctx.send(embed=embed)
            else:
                print(" " * console_width, end="\r")
                log_print(
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
                    timestamp=datetime.datetime.now()
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
            print(" " * console_width, end="\r")
            log_print(
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
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
            embed.set_thumbnail(url=pfp)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Watch(bot))