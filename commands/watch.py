import datetime
from discord.ext import commands
import aiohttp
from colorama import Fore
import discord
from Functions.Sql_handler import SQLiteHandler
import Functions.others
import re
import asyncio

ch = SQLiteHandler()


class Watch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.COLOR_SUCCESS = 65280
        self.COLOR_WARNING = 16776960
        self.COLOR_ERROR = 16711680

    @commands.command(
        name="watch",
        aliases=["w"],
        usage="watch <streamername_or_link> [<streamername_or_link> <streamername_or_link>...]",
        help="Add streamers to your watch list (provide one or more streamer names or links)",
    )
    async def watch(self, ctx, *args):
        variables = Functions.others.unpickle_variable()
        self.VERSION = variables["version"]
        AUTHORIZATION = variables["authorization"]
        CLIENT_ID = variables["client_id"]
        self.streamer_data_cache = variables["streamers_cache"]

        streamers_data = []
        failed_streamers = set()
        already_in_list = []
        not_registered = []
        streamer_names_added = []

        async def process_streamer(session, streamer_name_or_link):
            if "https://www.twitch.tv/" in streamer_name_or_link:
                streamer_name = re.search(
                    r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
                ).group(1)
                streamer_name = streamer_name.lower()
            else:
                streamer_name = streamer_name_or_link.lower()

            if streamer_name in self.streamer_data_cache:
                pfp = self.streamer_data_cache[streamer_name]["profile_image_url"]
            else:
                url = f"https://api.twitch.tv/helix/users?login={streamer_name}"
                headers = {
                    "Client-ID": f"{CLIENT_ID}",
                    "Authorization": f"Bearer {AUTHORIZATION}",
                }
                async with session.get(url, headers=headers) as response:
                    data = await response.json()
                print(data)

                if not data["data"]:
                    Functions.others.log_print(
                        Fore.CYAN
                        + Functions.others.get_timestamp()
                        + Fore.RESET
                        + " "
                        + Fore.RED
                        + Functions.others.holders(2)
                        + f"{Fore.CYAN + streamer_name + Fore.RESET} Twitch profile not found."
                        + Fore.RESET,
                        show_message=False
                    )
                    failed_streamers.add(streamer_name)
                    return
                pfp = data["data"][0]["profile_image_url"]
            user_id = str(ctx.author.id)
            user_ids = ch.get_all_user_ids()
            if user_id in user_ids:
                streamer_list = ch.get_streamers_for_user(user_id)
                if streamer_name not in streamer_list:
                    ch.add_streamer_to_user(user_id, streamer_name.strip())
                    streamer_list.append(streamer_name.strip())
                    if streamer_name not in streamer_names_added:
                        streamer_names_added.append(streamer_name)
                    Functions.others.log_print(
                        Fore.CYAN
                        + Functions.others.get_timestamp()
                        + Fore.RESET
                        + " "
                        + Fore.LIGHTGREEN_EX
                        + Functions.others.holders(1)
                        + f"Added {Fore.CYAN + streamer_name + Fore.RESET} to user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist."
                        + Fore.RESET,
                        show_message=False
                    )
                    streamers_data.append({
                        "streamer_name": streamer_name,
                        "pfp": pfp
                    })
                else:
                    Functions.others.log_print(
                        Fore.CYAN
                        + Functions.others.get_timestamp()
                        + Fore.RESET
                        + " "
                        + f"{Fore.CYAN + streamer_name + Fore.RESET} is already in user {Fore.CYAN + ctx.author.name + Fore.RESET}'s watchlist.",
                        show_message=False
                    )
                    already_in_list.append({
                        "streamer_name": streamer_name,
                        "pfp": pfp
                    })
            else:
                ch.add_user(
                    user_data={
                        "discord_username": ctx.author.name,
                        "discord_id": user_id,
                        "streamer_list": [streamer_name.strip()],
                    }
                )
                streamers_data.append({
                    "streamer_name": streamer_name,
                    "pfp": pfp
                })
                Functions.others.log_print(
                    Fore.CYAN
                    + Functions.others.get_timestamp()
                    + Fore.RESET
                    + " "
                    + Fore.LIGHTGREEN_EX
                    + Functions.others.holders(1)
                    + f"Created a new watchlist for user {Fore.CYAN + ctx.author.name + Fore.RESET}."
                    + Fore.RESET,
                    show_message=False
                )
                not_registered.append(True)

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[process_streamer(session, streamer) for streamer in args]
            )

        streamer_data = [streamer for streamer in streamers_data if streamer]

        if not streamer_data and not streamers_data and not already_in_list and not failed_streamers:
            return

        title = description = color = None
        if not_registered:
            title = f"Created a new watchlist for {ctx.author.name} and added the streamers! "
            description = "**Added the following streamers:**"
            color = 65280  # green color for success
        elif streamers_data:
            title = f"Added streamers to your watchlist! {ctx.author.name}"
            # Include the names
            description = f"**Added the following streamers:**\n{', '.join(streamer_names_added)}"
            color = 65280  # green color for success
        elif already_in_list and not failed_streamers:
            title = "No streamers added"
            description = "All the streamers you tried to add are already in your list."
            color = 16776960  # yellow color for warning
        elif failed_streamers and not already_in_list:
            title = "No streamers added"
            description = "No valid streamers found."
            color = 16711680  # red color for error
        else:
            title = "No streamers added"
            description = "No valid streamers found and all the streamers you tried to add are already in your list."
            color = 16711680  # red color for error

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"{self.VERSION} | Made by Beelzebub2")

        if failed_streamers:
            failed_streamers_str = "\n".join(failed_streamers)
            embed.add_field(name="Failed streamers",
                            value=f"Couldn't find:\n{failed_streamers_str}")

        if already_in_list:
            already_in_list_str = "\n".join(
                [item["streamer_name"] for item in already_in_list])
            embed.add_field(name="Already in your list",
                            value=f"\n{already_in_list_str}")

        if streamers_data:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Watch(bot))
