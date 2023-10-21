from discord.ext import commands
import discord
import datetime
import Functions.others
from Functions.Sql_handler import SQLiteHandler
import os
import psutil


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
        cached_streamers = variables["streamers_cache"]
        db_size = os.path.getsize("data.db")
        formatted_db_size = self.format_file_size(db_size)
        current_time = datetime.datetime.now()
        start_time = datetime.datetime.strptime(ch.get_time(), date_format)
        uptime = current_time - start_time
        uptime = str(uptime).split(".")[0]
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_usage = self.get_memory_usage()

        embed = discord.Embed(title="Bot Stats", color=discord.Color.green(
        ), timestamp=datetime.datetime.now())
        embed.add_field(name="Uptime", value=f"{uptime}")
        embed.add_field(name="Users", value=len(ch.get_all_user_ids()))
        embed.add_field(name="Streamers", value=len(ch.get_all_streamers()))
        embed.add_field(name="Loaded commands", value=len(working_commands))
        embed.add_field(name="Failed commands", value=len(failed_commands))
        embed.add_field(name="Database Size", value=formatted_db_size)
        embed.add_field(name="Cached Streamers", value=len(cached_streamers))
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%")
        embed.add_field(name="Memory Usage", value=memory_usage)
        await ctx.send(embed=embed)

    def format_file_size(self, size_in_bytes):
        size_in_bytes = float(size_in_bytes)
        size_units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        while size_in_bytes >= 1024 and unit_index < len(size_units) - 1:
            size_in_bytes /= 1024
            unit_index += 1
        return f"{size_in_bytes:.2f} {size_units[unit_index]}"

    def get_memory_usage(self):
        pid = os.getpid()
        python_process = psutil.Process(pid)
        size_in_bytes = float(python_process.memory_info()[
                              0])  # memory use in bytes

        size_units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        while size_in_bytes >= 1024 and unit_index < len(size_units) - 1:
            size_in_bytes /= 1024
            unit_index += 1
        return f"{size_in_bytes:.2f} {size_units[unit_index]}"


async def setup(bot):
    await bot.add_cog(Stats(bot))
