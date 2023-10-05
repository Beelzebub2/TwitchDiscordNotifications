from discord.ext import commands
import discord
import datetime
import pickle

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

VERSION = variables["version"]

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["h", "commands", "command"],
        usage="help",
        help="Shows all the available commands and their descriptions",
    )
    async def list_commands(self, ctx):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are the available commands, their descriptions, and usage:",
            color=65280,
            timestamp=datetime.datetime.now()
        )
        

        sorted_commands = sorted(self.bot.commands, key=lambda x: x.name)

        for command in sorted_commands:
            if command.hidden:
                continue

            description = command.help or "No description available."
            aliases = ", ".join(command.aliases) if command.aliases else "No aliases"
            usage = command.usage or f"No usage specified for {command.name}"

            embed.add_field(
                name=f"**{command.name.capitalize()}**",
                value=f"Description: {description}\nUsage: `{usage}`\nAliases: {aliases}",
                inline=False,
            )

        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))