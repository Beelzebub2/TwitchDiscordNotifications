import datetime
from discord.ext import commands
import discord
from colorama import Fore
from functions.Sql_handler import SQLiteHandler
import functions.others

variables = functions.others.unpickle_variable()

ch = SQLiteHandler("data.db")
console_width = variables["console_width"]
intents = variables["intents"]


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''On Guild Join'''
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # TODO add embed and log_print
        in_guild = ch.is_guild_in_config(guild.id)
        if not in_guild:
            ch.create_new_guild_template(guild.id, guild.name)

    '''On Guild Remove'''
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # TODO add embed and log_print
        in_guild = ch.is_guild_in_config(guild.id)
        if in_guild:
            ch.remove_guild(guild.id)

    '''On Member Join'''
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id

        role_id = int(ch.get_role_to_add(guild_id))
        general_channel = member.guild.text_channels[0]

        if not role_id:
            await general_channel.send(
                f"Welcome {member.mention} to the server, but it seems the server administrator has not configured the role assignment. Please contact an admin for assistance."
            )
        else:
            role = member.guild.get_role(role_id)
            if role:
                if role not in member.roles:
                    await member.add_roles(role)
                    print(" " * console_width, end="\r")
                    functions.others.log_print(
                        f"{functions.others.get_timestamp()} Assigned role named {role.name} to {member.display_name} in the target guild."
                    )
            else:
                await general_channel.send(
                    f"Welcome {member.mention} to the server, but the configured role with ID {role_id} does not exist. Please contact an admin to update the role ID."
                )

    # TODO Better error handler
    '''On Command Error'''
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            command = ctx.message.content.split()
            prefix = await self.bot.get_prefix(ctx.message)
            if len(command) >= 2:
                command = ctx.message.content.split(" ")[1]
            else:
                command = ctx.message.content.split(" ")[0]

            print(" " * console_width, end="\r")
            functions.others.log_print(
                Fore.CYAN
                + functions.others.get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + "[ERROR] "
                + f"Command {Fore.CYAN + command + Fore.RESET} doesn't exist."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Command not found",
                description=f"Command **__{command}__** does not exist. Use .help for more info.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            remaining_time = round(error.retry_after)
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"Please wait {remaining_time} seconds before trying again.",
                color=0xFF0000
            )
            embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
            await ctx.send(embed=embed)

        else:
            print(" " * console_width, end="\r")
            functions.others.log_print(
                Fore.CYAN
                + functions.others.get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + "[ERROR] "
                + f"Error: {error}"
                + Fore.RESET
            )

    '''On Message'''
    @commands.Cog.listener()
    async def on_message(self, message):
        import discord
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            if isinstance(message.channel, discord.DMChannel):
                embed = discord.Embed(
                    title=f"Hello, {message.author.display_name}!",
                    description=f"My prefix is: `{ch.get_prefix()}`",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )

            elif isinstance(message.channel, discord.TextChannel):
                guild_prefix = self.bot.command_prefix
                if message.guild:
                    guild_prefix = ch.get_guild_prefix(message.guild.id)

                embed = discord.Embed(
                    title=f"Hello, {message.author.display_name}!",
                    description=f"My prefix for this server is: `{guild_prefix}`",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bot_exit(self):
        functions.others.custom_interrupt_handler()


async def setup(bot):
    await bot.add_cog(Events(bot))
