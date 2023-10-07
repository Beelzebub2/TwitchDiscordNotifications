from discord.ext import commands
import discord
import datetime
import pickle
import functions.others

variables = functions.others.unpickle_variable()

VERSION = variables["version"]

class CommandNotFoundError(commands.CommandNotFound):
    pass

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["h", "commands", "command"],
        usage="help [command]",
        help="Shows all the available commands and their descriptions, or specific command information if a command is provided.",
    )
    async def list_commands(self, ctx, command=None):
        if not command:
            # Display all commands
            embed = discord.Embed(
                title="Bot Commands",
                description="Here are the available commands, their descriptions, and usage:",
                color=65280,
                timestamp=datetime.datetime.now()
            )

            sorted_commands = sorted(self.bot.commands, key=lambda x: x.name)

            for cmd in sorted_commands:
                if cmd.hidden:
                    continue

                description = cmd.help or "No description available."
                aliases = ", ".join(
                    cmd.aliases) if cmd.aliases else "No aliases"
                usage = cmd.usage or f"No usage specified for {cmd.name}"

                embed.add_field(
                    name=f"**{cmd.name.capitalize()}**",
                    value=f"Description: {description}\nUsage: `{usage}`\nAliases: {aliases}",
                    inline=False,
                )

            embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
            await ctx.send(embed=embed)
        else:
            cmd = self.bot.get_command(command)

            if cmd:
                embed = discord.Embed(
                    title=f"Command: {cmd.name.capitalize()}",
                    description=cmd.help or "No description available.",
                    color=65280,
                    timestamp=datetime.datetime.now()
                )

                aliases = ", ".join(
                    cmd.aliases) if cmd.aliases else "No aliases"
                usage = cmd.usage or f"No usage specified for {cmd.name}"

                embed.add_field(
                    name="Usage",
                    value=f"`{usage}`",
                    inline=False,
                )

                embed.add_field(
                    name="Aliases",
                    value=aliases,
                    inline=False,
                )

                embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
                await ctx.send(embed=embed)
            else:
                raise CommandNotFoundError(f"Command '{command}' not found.")


async def setup(bot):
    await bot.add_cog(Help(bot))
