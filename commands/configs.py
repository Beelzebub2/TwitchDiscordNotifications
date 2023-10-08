from discord.ext import commands
import discord
from Functions.Sql_handler import SQLiteHandler

ch = SQLiteHandler("data.db")

'''This class has 2 different commands
   for the sake of simplicity'''


class Configs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''Configrole command'''
    @commands.command(
        name="configrole",
        aliases=["cr"],
        usage="configrole <@role>",
        help="Change the role to add in the server configuration",
    )
    async def prefix_config_role(self, ctx, role: discord.Role):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(
                "You do not have the necessary permissions to use this command."
            )
            return
        guild_id = ctx.guild.id
        role_id = role.id
        ch.change_role_to_add(guild_id, role_id)
        await ctx.send(
            f"The role to add has been updated to {role.mention} in the server configuration."
        )

    '''ConfigPrefix command'''
    @commands.command(
        name="configprefix",
        aliases=["cx"],
        usage="configprefix <new_prefix>",
        help="changes the default prefix of the guild",
    )
    async def change_guild_prefix(self, ctx, new_prefix: str):
        if ctx.author.guild_permissions.administrator:
            guild_id = ctx.guild.id
            ch.change_guild_prefix(guild_id, new_prefix)
            await ctx.send(f"Prefix for this guild has been updated to `{new_prefix}`.")
        else:
            await ctx.send(
                "You do not have the necessary permissions to change the prefix."
            )


async def setup(bot):
    await bot.add_cog(Configs(bot))
