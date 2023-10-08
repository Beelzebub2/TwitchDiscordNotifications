from discord.ext import commands
import discord
import datetime
import Functions.others

variables = Functions.others.unpickle_variable()

VERSION = variables["version"]


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="invite",
        aliases=["i"],
        help="Generates bot invite link",
        usage="invite",
    )
    async def invite(self, ctx):
        embed = discord.Embed(
            title="Invite Me!",
            description=f"[Click here](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot)",
            color=65280,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Invite(bot))
