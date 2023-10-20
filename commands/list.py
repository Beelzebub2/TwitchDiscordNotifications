from discord.ext import commands
import Functions.others
import discord
import aiohttp
import asyncio
from colorama import Fore
import math
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os
import datetime
from Functions.Sql_handler import SQLiteHandler
ch = SQLiteHandler("data.db")


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
                pfps = []
                names = []
                async with aiohttp.ClientSession() as session:
                    await asyncio.gather(
                        *[
                            self.fetch_streamer_data(
                                session, streamer, pfps, names)
                            for streamer in streamer_list
                        ]
                    )

                num_pfps = len(pfps)
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

                combined_image_height = num_rows * \
                    (image_height + name_box_height)

                combined_image = Image.new(
                    "RGB", (combined_image_width, combined_image_height)
                )

                x_offset = 0
                y_offset = name_box_height

                for i, (pfp_url, name) in enumerate(zip(pfps, names)):
                    pfp_response = requests.get(pfp_url)
                    pfp_image = Image.open(io.BytesIO(pfp_response.content))
                    pfp_image.thumbnail((image_width, image_height))

                    name_x = x_offset
                    name_y = y_offset - name_box_height

                    combined_image.paste(pfp_image, (x_offset, y_offset))

                    name_box = Image.new(
                        "RGB", (name_box_width, name_box_height), name_box_color
                    )

                    draw = ImageDraw.Draw(name_box)
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

                embed = discord.Embed(
                    title=f"Your Streamers {ctx.author.name}",
                    description=f"**You are currently watching the following streamers:**",
                    color=10242047,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"{self.VERSION} | Made by Beelzebub2")
                embed.set_image(url="attachment://combined_image.png")

                with open("combined_image.png", "rb") as img_file:
                    file = discord.File(img_file)
                    await ctx.channel.send(file=file, embed=embed)
                os.remove("combined_image.png")

                return streamer_names, combined_image

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
                await ctx.channel.send(embed=embed)
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
            await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ListStreamers(bot))
