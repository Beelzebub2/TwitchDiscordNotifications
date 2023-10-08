import datetime
from discord.ext import commands
import sys
import os
import discord
from Functions.Sql_handler import SQLiteHandler
import Functions.others


ch = SQLiteHandler("data.db")


class Restart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="restart",
        aliases=["rr"],
        help="Restarts Bot.",
        usage="restart",
        hidden=True,
    )
    @commands.is_owner()
    async def restart(self, ctx):
        variables = Functions.others.unpickle_variable()
        processed_streamers = variables["processed_streamers"]
        data = {"Restarted": True, "Streamers": processed_streamers}
        ch.save_to_temp_json(data)
        embed = discord.Embed(
            title="Restarting",
            description="Bot is restarting...",
            color=0x00FF00,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
        await ctx.send(embed=embed)

        python = sys.executable
        print(python)
        os.execl(python, python, *sys.argv)


async def setup(bot):
    await bot.add_cog(Restart(bot))
