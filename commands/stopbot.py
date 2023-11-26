from discord.ext import commands
import discord


class StopBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='stop',
        description='Stop the bot (bot owner only)',
        usage='stop',
        hidden=True
    )
    @commands.is_owner()
    async def stop_bot(self, ctx):
        embed = discord.Embed(
            title='Bot Shutdown',
            description='The bot is stopping...',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        try:
            await self.bot.close()
        except:
            pass


async def setup(bot):
    await bot.add_cog(StopBot(bot))
