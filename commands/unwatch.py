import datetime
from discord.ext import commands
from colorama import Fore
import discord
from Functions.Sql_handler import SQLiteHandler
from Functions.others import get_timestamp, log_print
import re
import Functions.others

ch = SQLiteHandler("data.db")

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

        variables = Functions.others.unpickle_variable()
        VERSION = variables["version"]
        if "https://www.twitch.tv/" in streamer_name_or_link:
            streamer_name = re.search(
                r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
            ).group(1)
            streamer_name = streamer_name.lower()
        else:
            streamer_name = streamer_name_or_link.lower()

        user_id = str(ctx.author.id)
        user_ids = ch.get_all_user_ids()
        variables = Functions.others.unpickle_variable()
        console_width = variables["console_width"]
        if user_id in user_ids:
            streamer_list = ch.get_streamers_for_user(user_id)
            if any(streamer_name.lower() == s.lower() for s in streamer_list):
                ch.remove_streamer_from_user(user_id, streamer_name)
                print(" " * console_width, end="\r")
                log_print(
                    Fore.CYAN
                    + get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTGREEN_EX
                    + "[SUCCESS] "
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
                    + Fore.RED
                    + "[ERROR] "
                    + f"{Fore.CYAN + streamer_name + Fore.RESET} is not in user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist."
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description=f"{streamer_name} is not in your watchlist.",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
                await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UnWatch(bot))
