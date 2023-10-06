import datetime
from discord.ext import commands
from colorama import Fore
import discord
from functions.Sql_handler import SQLiteHandler
from functions.others import get_timestamp, log_print
import re
import pickle

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

ch = SQLiteHandler("data.db")
console_width = variables["console_width"]
processed_streamers = variables["processed_streamers"]
VERSION = variables["version"]

# TODO Accept multiple streamers


class UnWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="unwatch",
        aliases=["u"],
        usage="unwatch <streamername_or_link>",
        help="Removes the streamer from your watch list (provide either streamer name or link)",
    )
    async def unwatch(self, ctx, streamer_name_or_link: str):
        if "https://www.twitch.tv/" in streamer_name_or_link:
            streamer_name = re.search(
                r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
            ).group(1)
            streamer_name = streamer_name.lower()
        else:
            streamer_name = streamer_name_or_link.lower()

        user_id = str(ctx.author.id)
        user_ids = ch.get_all_user_ids()
        if user_id in user_ids:
            streamer_list = ch.get_streamers_for_user(user_id)
            print(streamer_list)
            print(len(streamer_list))
            if any(streamer_name.lower() == s.lower() for s in streamer_list):
                ch.remove_streamer_from_user(user_id, streamer_name)
                if (
                    streamer_name in processed_streamers
                    and streamer_name not in ch.get_all_streamers()
                ):
                    processed_streamers.remove(streamer_name.lower())
                print(" " * console_width, end="\r")
                log_print(
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
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.channel.send(embed=embed)
            else:
                print(" " * console_width, end="\r")
                log_print(
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
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UnWatch(bot))
