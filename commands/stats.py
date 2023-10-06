from discord.ext import commands
import discord
import datetime
import pickle

from functions.Sql_handler import SQLiteHandler

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

ch = SQLiteHandler("data.db")
date_format = variables["date_format"]


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats", aliases=["st"], help="Shows Bots stats.", usage="stats")
    async def stats(self, ctx):
        current_time = datetime.datetime.now()
        start_time = datetime.datetime.strptime(ch.get_time(), date_format)
        uptime = current_time - start_time
        uptime = str(uptime).split(".")[0]
        embed = discord.Embed(title="Bot Stats", color=discord.Color.green(
        ), timestamp=datetime.datetime.now())
        embed.add_field(name="Uptime", value=f"My current uptime is {uptime}")
        embed.add_field(name="Users", value=len(ch.get_all_user_ids()))
        embed.add_field(name="Streamers", value=len(ch.get_all_streamers()))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
