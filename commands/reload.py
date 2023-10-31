import os
from discord.ext import commands
import discord
import datetime
from Functions.Sql_handler import SQLiteHandler

ch = SQLiteHandler()


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload", aliases=["r"], description="reloads cogs")
    @commands.is_owner()
    async def reload(self, ctx):
        Loaded_commands = []
        Failed_commands = []

        extension_files = [filename[:-3]
                           for filename in os.listdir('./commands') if filename.endswith('.py')]
        for filename in extension_files:
            try:
                await self.bot.reload_extension(f'commands.{filename}')
                Loaded_commands.append(filename)
            except:
                Failed_commands.append(filename)
        threshold = (len(Loaded_commands) - len(Failed_commands))

        bot_info = await self.bot.application_info()
        owner_id = str(bot_info.owner.id)
        ch.save_bot_owner_id(owner_id)
        owner = self.bot.get_user(int(owner_id))
        if threshold <= 0:
            title = "Error Reloading the commands"
            description = "Failed reloading most/all of the commands"
            url = "https://i.imgur.com/lmVQboe.png"
            color = discord.Color.red()
        else:
            title = "Commands Reloaded"
            description = "Reloaded most/all of the commands"
            url = "https://i.imgur.com/TavP95o.png"
            color = 0x00FF00
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.datetime.now()
        )
        if len(Failed_commands) == 0 or len(Failed_commands) == None:
            value = "0"
        else:
            value = "\n".join(Failed_commands)
        embed.set_thumbnail(url=url)
        embed.add_field(name="Loaded", value=len(Loaded_commands))
        embed.add_field(name="Failed",
                        value=value)
        await owner.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Reload(bot))
