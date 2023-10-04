from discord.ext import commands
from discord import Color, Embed
from datetime import datetime
import pickle

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

ch = variables["ch"]
date_format = variables["date_format"]

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats", aliases=["st"], help="Shows Bots stats.", usage="stats")
    async def stats(self, ctx):
        current_time = datetime.now()
        start_time = datetime.strptime(ch.get_time(), date_format)
        uptime = current_time - start_time
        uptime = str(uptime).split(".")[0]
        embed = Embed(title="Bot Stats", color=Color.green())
        embed.add_field(name="Uptime", value=f"My current uptime is {uptime}")
        embed.add_field(name="Users", value=len(ch.get_all_user_ids()))
        embed.add_field(name="Streamers", value=len(ch.get_all_streamers()))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))