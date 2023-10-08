from discord.ext import commands
import discord
import datetime
import Functions.others
from Functions.Sql_handler import SQLiteHandler
import os


ch = SQLiteHandler("data.db")


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats", aliases=["st"], help="Shows Bots stats.", usage="stats")
    async def stats(self, ctx):
        variables = Functions.others.unpickle_variable()
        working_commands = variables["loaded_commands"]
        failed_commands = variables["failed_commands"]
        date_format = variables["date_format"]
        db_size = os.path.getsize("data.db")
        db_size = db_size / (1024 * 1024)
        current_time = datetime.datetime.now()
        start_time = datetime.datetime.strptime(ch.get_time(), date_format)
        uptime = current_time - start_time
        uptime = str(uptime).split(".")[0]
        embed = discord.Embed(title="Bot Stats", color=discord.Color.green(
        ), timestamp=datetime.datetime.now())
        embed.add_field(name="Uptime", value=f"My current uptime is {uptime}")
        embed.add_field(name="Users", value=len(ch.get_all_user_ids()))
        embed.add_field(name="Streamers", value=len(ch.get_all_streamers()))
        embed.add_field(name="Loaded commands", value=len(working_commands))
        embed.add_field(name="Failed commands", value=len(failed_commands))
        embed.add_field(name="Database Size", value=f"{db_size:.2f}mb")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
