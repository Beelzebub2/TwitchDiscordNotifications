import datetime
from discord.ext import commands
from colorama import Fore
import discord
from Functions.Sql_handler import SQLiteHandler
import re
import Functions.others

ch = SQLiteHandler("data.db")


class UnWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="unwatch",
        aliases=["u"],
        usage="unwatch <streamername_or_link> [<streamername_or_link> <streamername_or_link>...]",
        help="Removes streamers from your watch list (provide one or more streamer names or links)",
    )
    async def unwatch(self, ctx, *streamer_names_or_links):
        variables = Functions.others.unpickle_variable()
        VERSION = variables["version"]
        removed_streamers = []
        not_in_watchlist = []

        user_id = str(ctx.author.id)
        user_ids = ch.get_all_user_ids()

        for streamer_name_or_link in streamer_names_or_links:
            if "https://www.twitch.tv/" in streamer_name_or_link:
                streamer_name = re.search(
                    r"https://www.twitch.tv/([^\s/]+)", streamer_name_or_link
                ).group(1)
                streamer_name = streamer_name.lower()
            else:
                streamer_name = streamer_name_or_link.lower()

            if user_id in user_ids:
                streamer_list = ch.get_streamers_for_user(user_id)
                if any(streamer_name.lower() == s.lower() for s in streamer_list):
                    ch.remove_streamer_from_user(user_id, streamer_name)
                    removed_streamers.append(streamer_name)
                else:
                    not_in_watchlist.append(streamer_name)

        title = description = color = None
        if removed_streamers and not not_in_watchlist:
            title = "Streamers removed from your watchlist"
            color = 65280  # green color for success
        elif not_in_watchlist and not removed_streamers:
            title = "No streamers removed"
            description = "The streamers you tried to remove are not in your watchlist."
            color = 16776960  # yellow color for warning
        elif removed_streamers and not_in_watchlist:
            title = "Some streamers removed"
            description = "Removed some streamers, but some were not in your watchlist."
            color = 16776960  # yellow color for warning
        else:
            title = "No streamers removed"
            description = "No valid streamers found."
            color = 16711680  # red color for error

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"{VERSION} | Made by Beelzebub2")

        if removed_streamers:
            removed_streamers_str = "\n".join(removed_streamers)
            embed.add_field(name="Removed Streamers",
                            value=f"{removed_streamers_str}")

        if not_in_watchlist:
            not_in_watchlist_str = "\n".join(not_in_watchlist)
            embed.add_field(name="Not in Watchlist",
                            value=f"{not_in_watchlist_str}")

        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UnWatch(bot))
