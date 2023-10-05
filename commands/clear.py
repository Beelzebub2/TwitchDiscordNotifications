import asyncio
from discord.ext import commands
import discord
import datetime
import pickle
import functions.others

with open("variables.pkl", "rb") as file:
    variables = pickle.load(file)

VERSION = variables["version"]
HEADERS = variables["headers"]
console_width = variables["console_width"]

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="clear",
        aliases=["c"],
        help="Clears all the messages sent by the bot",
        usage="clear",
    )
    async def clear_bot_messages(self, ctx):
        messages_to_remove = 1000
        user = await self.bot.fetch_user(ctx.author.id)

        async for message in ctx.history(limit=messages_to_remove):
            if message.author.id == self.bot.user.id:
                await message.delete()
                await asyncio.sleep(1)

        # Create and send an embed message
        embed = discord.Embed(
            title="Conversation Cleared",
            description="All messages have been cleared.",
            color=65280,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")
        await ctx.send(embed=embed)

    async def fetch_streamer_data(session, streamer_name, pfps, names):
        streamer_name = streamer_name.replace(" ", "")
        url = f"https://api.twitch.tv/helix/users?login={streamer_name}"

        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    streamer_data = data["data"][0]
                    profile_picture_url = streamer_data.get("profile_image_url", "")
                    profile_picture_url = profile_picture_url.replace(
                        "{width}", "150"
                    ).replace("{height}", "150")
                    pfps.append(profile_picture_url)
                    names.append(streamer_data["display_name"])
                else:
                    print(" " * console_width, end="\r")
                    functions.others.log_print(
                        f"{functions.others.get_timestamp()} No data found for streamer: {streamer_name}"
                    )
    

async def setup(bot):
    await bot.add_cog(Clear(bot))