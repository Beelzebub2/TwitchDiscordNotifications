import asyncio
from discord.ext import commands
import discord
import datetime
import pickle
import functions.others

variables = functions.others.unpickle_variable()

VERSION = variables["version"]
HEADERS = variables["headers"]
console_width = variables["console_width"]


class Clear(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="clear",
        aliases=["c"],
        help="Clears all the messages sent by the bot",
        usage="clear",
    )
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def clear_bot_messages(self, ctx) -> None:
        messages_to_remove = 1000
        user = await self.bot.fetch_user(ctx.author.id)

        messages = []
        async for message in ctx.history(limit=messages_to_remove):
            if message.author.id == self.bot.user.id:
                messages.append(message)
        for message in messages:
            await message.delete()
            await asyncio.sleep(1)

        embed = discord.Embed(
            title="Conversation Cleared",
            description="All messages have been cleared.",
            color=0x00FF00,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
        embed.set_thumbnail(url="https://i.imgur.com/TavP95o.png")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Clear(bot))
