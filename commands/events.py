import datetime
from discord.ext import commands
from functions.others import get_timestamp, log_print
import pickle

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

ch = variables["ch"]
console_width = variables["console_width"]
intents = variables["intents"]

bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(ch.get_prefix), intents=intents
    )

'''All bot events that didn't need to be on main file'''

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''On Guild Join'''
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not ch.is_guild_in_config(guild.id):
            ch.create_new_guild_template(guild.id, guild.name)

    '''On Guild Remove'''
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if ch.is_guild_in_config():
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
                    log_print(
                        f"{get_timestamp()} Assigned role named {role.name} to {member.display_name} in the target guild."
                    )
            else:
                await general_channel.send(
                    f"Welcome {member.mention} to the server, but the configured role with ID {role_id} does not exist. Please contact an admin to update the role ID."
                )

    '''On Command Error'''
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        from colorama import Fore
        import discord
        if isinstance(error, commands.CommandNotFound):
            command = ctx.message.content
            print(" " * console_width, end="\r")
            log_print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"Command {Fore.CYAN + command + Fore.RESET} doesn't exist."
                + Fore.RESET
            )
            embed = discord.Embed(
                title="Command not found",
                description=f"Command **__{command}__** does not exist use .help for more info.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url="https://i.imgur.com/lmVQboe.png")
            await ctx.send(embed=embed)
        else:
            print(" " * console_width, end="\r")
            log_print(
                Fore.CYAN
                + get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"Error: {error}"
                + Fore.RESET
            )
    
    '''On Message'''
    @commands.Cog.listener()
    async def on_message(self, message):
        import discord
        if message.author == bot.user:
            return

        if bot.user.mentioned_in(message):
            if isinstance(message.channel, discord.DMChannel):
                embed = discord.Embed(
                    title=f"Hello, {message.author.display_name}!",
                    description=f"My prefix is: `{ch.get_prefix()}`",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )

            elif isinstance(message.channel, discord.TextChannel):
                guild_prefix = bot.command_prefix
                if message.guild:
                    guild_prefix = ch.get_guild_prefix(message.guild.id)

                embed = discord.Embed(
                    title=f"Hello, {message.author.display_name}!",
                    description=f"My prefix for this server is: `{guild_prefix}`",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
            await message.channel.send(embed=embed)

        await bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Events(bot))