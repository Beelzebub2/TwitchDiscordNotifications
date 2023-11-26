import datetime
import traceback
from discord.ext import commands
import discord
from colorama import Fore
from Functions.Sql_handler import SQLiteHandler
import Functions.others


ch = SQLiteHandler()


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
        variables = Functions.others.unpickle_variable()
        console_width = variables["console_width"]

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

                    Functions.others.log_print(
                        f"{Functions.others.get_timestamp()}{Functions.others.holders(3)} Assigned role named {role.name} to {member.display_name} in the target guild.", show_message=False
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
            full_command = ctx.message.content
            error_message = f"Command '{full_command}' is not valid."
            embed_title = "Command not found"
            embed_description = f"Command '{full_command}' is not valid. Use {ctx.prefix}help for more info."

        elif isinstance(error, commands.MissingRequiredArgument):
            param_name = error.param.name
            error_message = f"Parameter '{param_name}' is missing for the command."
            embed_title = "Missing Parameter"
            embed_description = f"Parameter '{param_name}' is required for the command. Use {ctx.prefix}help for more info."

        elif isinstance(error, commands.BadArgument):
            error_message = f"Invalid parameter: {error}"
            embed_title = "Invalid Parameter"
            embed_description = f"Invalid parameter: {error}. Use {ctx.prefix}help for more info."

        elif isinstance(error, commands.CommandOnCooldown):
            remaining_time = round(error.retry_after)
            error_message = f"Command on Cooldown: Please wait {remaining_time} seconds before trying again."
            embed_title = "Command on Cooldown"
            embed_description = error_message

        else:
            traceback_info = traceback.format_exception(
                type(error), error, error.__traceback__)
            error_message = f"Error: {error}\n{''.join(traceback_info)}"

        Functions.others.log_print(
            f"{Fore.CYAN}{Functions.others.get_timestamp()}{Fore.RESET} {Fore.RED}{Functions.others.holders(2)} {error_message}{Fore.RESET}",
            show_message=False
        )

        embed = discord.Embed(
            title=embed_title,
            description=embed_description,
            color=discord.Color.red() if "Command not found" in embed_title else 0xFF0000,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
        await ctx.send(embed=embed)

    '''On Message'''
    @commands.Cog.listener()
    async def on_message(self, message):
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


async def setup(bot):
    await bot.add_cog(Events(bot))
