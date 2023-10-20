import datetime
import os
from discord.ext import commands
import aiohttp
from colorama import Fore
import discord
import requests
from Functions.Sql_handler import SQLiteHandler
import Functions.others
import re
from PIL import Image, ImageDraw, ImageFont
import io
import math
import asyncio

ch = SQLiteHandler("data.db")


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

                if not data["data"]:
                    Functions.others.log_print(
                        Fore.CYAN
                        + Functions.others.get_timestamp()
                        + Fore.RESET
                        + " "
                        + Fore.RED
                        + "[ERROR] "
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
                    Functions.others.log_print(
                        Fore.CYAN
                        + Functions.others.get_timestamp()
                        + Fore.RESET
                        + " "
                        + Fore.LIGHTGREEN_EX
                        + "[SUCCESS] "
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
                    + "[SUCCESS] "
                    + f"Created a new watchlist for user {Fore.CYAN + ctx.author.name + Fore.RESET}."
                    + Fore.RESET
                )
                not_registered.append(True)

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[process_streamer(session, streamer) for streamer in args]
            )

        streamer_data = [streamer for streamer in streamers_data if streamer]

        if not streamer_data and not streamers_data and not already_in_list and not failed_streamers:
            return

        if streamers_data:
            num_pfps = len(streamers_data)
            max_images_per_row = 5
            image_width = 100
            image_height = 100
            num_rows = math.ceil(num_pfps / max_images_per_row)

            name_box_width = image_width
            name_box_height = 20
            name_box_color = (0, 0, 0)
            name_text_color = (255, 255, 255)
            font_size = 9
            font = ImageFont.truetype("arialbd.ttf", font_size)

            if num_pfps <= max_images_per_row:
                combined_image_width = num_pfps * image_width
            else:
                combined_image_width = max_images_per_row * image_width

            combined_image_height = num_rows * (image_height + name_box_height)

            combined_image = Image.new(
                "RGB", (combined_image_width, combined_image_height))

            x_offset = 0
            y_offset = name_box_height

            for i, streamer_data in enumerate(streamers_data):
                pfp_response = requests.get(streamer_data["pfp"])
                pfp_image = Image.open(io.BytesIO(pfp_response.content))
                pfp_image.thumbnail((image_width, image_height))

                name_x = x_offset
                name_y = y_offset - name_box_height

                combined_image.paste(pfp_image, (x_offset, y_offset))

                name_box = Image.new(
                    "RGB", (name_box_width, name_box_height), name_box_color)

                draw = ImageDraw.Draw(name_box)
                name = streamer_data["streamer_name"]
                text_bbox = draw.textbbox((0, 0), name, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = (name_box_width - text_width) // 2
                text_y = (name_box_height - text_height) // 2
                draw.text((text_x, text_y), name,
                          fill=name_text_color, font=font)

                combined_image.paste(name_box, (name_x, name_y))

                x_offset += image_width

                if x_offset >= combined_image_width:
                    x_offset = 0
                    y_offset += image_height + name_box_height

            combined_image.save("combined_image.png")
        title = description = color = None
        if not_registered:
            title = f"Created a new watchlist for {ctx.author.name} and added the streamers! "
            description = "**Added the following streamers:**"
            color = 65280  # green color for success
        elif streamers_data:
            title = f"Added streamers to your watchlist! {ctx.author.name}"
            description = "**Added the following streamers:**"
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
            with open("combined_image.png", "rb") as img_file:
                file = discord.File(img_file)
                embed.set_image(url="attachment://combined_image.png")
                await ctx.send(file=file, embed=embed)
            os.remove("combined_image.png")
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Watch(bot))
