from discord.ext import commands
import Functions.others
import discord
from colorama import Fore

import datetime
from Functions.Sql_handler import SQLiteHandler
ch = SQLiteHandler()


class ListStreamers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.others = Functions.others

    async def fetch_streamer_data(self, session, streamer_name, pfps, names):
        streamer_name = streamer_name.replace(" ", "")

        if streamer_name in self.streamer_data_cache:
            streamer_data = self.streamer_data_cache[streamer_name]
            profile_picture_url = streamer_data.get("profile_image_url", "")
            profile_picture_url = profile_picture_url.replace(
                "{width}", "150").replace("{height}", "150")
            pfps.append(profile_picture_url)
            names.append(streamer_data["display_name"])
        else:
            url = f"https://api.twitch.tv/helix/users?login={streamer_name}"
            async with session.get(url, headers=self.HEADERS) as response:
                if response.status == 200:
                    data = await response.json()
                    if "data" in data and len(data["data"]) > 0:
                        streamer_data = data["data"][0]
                        profile_picture_url = streamer_data.get(
                            "profile_image_url", "")
                        profile_picture_url = profile_picture_url.replace(
                            "{width}", "150").replace("{height}", "150")
                        pfps.append(profile_picture_url)
                        names.append(streamer_data["display_name"])
                    else:
                        self.others.log_print(
                            f"{self.others.get_timestamp()} No data found for streamer: {streamer_name}",
                            show_message=False
                        )

    @commands.command(
        name="list",
        aliases=["l"],
        help="Returns an embed with a list of all the streamers you're currently watching",
        usage="list",
    )
    async def list_streamers(self, ctx):
        user_id = str(ctx.author.id)
        user_ids = ch.get_all_user_ids()
        variables = self.others.unpickle_variable()
        self.VERSION = variables["version"]
        self.HEADERS = variables["headers"]
        self.streamer_data_cache = variables["streamers_cache"]

        if user_id in user_ids:
            streamer_list = ch.get_streamers_for_user(user_id)

            if streamer_list:
                streamer_names = ", ".join(streamer_list)

                self.others.log_print(
                    "\033[K"
                    + Fore.CYAN
                    + self.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTYELLOW_EX
                    + self.others.holders(3)
                    + ctx.author.name
                    + Fore.RESET
                    + f" requested their streamers: {len(streamer_list)}",
                    show_message=False
                )

                embed = discord.Embed(
                    title=f"Your Streamers {ctx.author.name}",
                    color=10242047,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{self.VERSION} | Made by Beelzebub2")

                embed.add_field(
                    name="Currently in your watchlist", value=streamer_names)

                await ctx.send(embed=embed)
            else:
                self.others.log_print(
                    Fore.CYAN
                    + self.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.YELLOW
                    + f"{Fore.CYAN + ctx.author.name + Fore.RESET} requested their streamers, but the watchlist is empty."
                    + Fore.RESET,
                    show_message=False
                )
                embed = discord.Embed(
                    title="Stream Watchlist",
                    description="Your watchlist is empty.",
                    color=16759808,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{self.VERSION} | Made by Beelzebub2")
                await ctx.send(embed=embed)
        else:
            self.others.log_print(
                Fore.CYAN
                + self.others.get_timestamp()
                + Fore.RESET
                + " "
                + Fore.RED
                + f"{Fore.CYAN + ctx.author.name + Fore.RESET} requested their streamers, but they don't have a watchlist yet."
                + Fore.RESET,
                show_message=False
            )
            embed = discord.Embed(
                title="Stream Watchlist",
                description="You don't have a watchlist yet.",
                color=16711680,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"{self.VERSION} | Made by Beelzebub2")
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ListStreamers(bot))
