import datetime
from discord.ext import commands
from colorama import Fore
import discord
from functions.Sql_handler import SQLiteHandler
from functions.others import log_print, get_timestamp
import pickle

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

ch = SQLiteHandler("data.db")
console_width = variables["console_width"]

class UnRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="unregister",
        aliases=["unreg"],
        help="Wipes out the watchlist.",
        usage="unregister",
    )
    async def unregister_user(self, ctx):
        user_id = str(ctx.author.id)

        if ch.delete_user(user_id):
            print(" " * console_width, end="\r")
            log_print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.YELLOW
                + f"{Fore.RED + ctx.author.name + Fore.RESET} Unregistered from bot."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Unregistration Successful",
                description="You have been unregistered from the bot.",
                color=0x00FF00,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
            await ctx.send(embed=embed)
        else:
            print(" " * console_width, end="\r")
            log_print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.YELLOW
                + f"{Fore.RED + ctx.author.name + Fore.RESET} Tried to unregister from bot but wasn't registered to begin with."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Unregistration Error",
                description="You are not registered with the bot.",
                color=0xFF0000,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UnRegister(bot))