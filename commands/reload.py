import asyncio
import os
import time
import discord
from discord.ext import commands
import concurrent.futures

# TODO make this shit work somehow


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def load_extension(self, filename):
        try:
            await self.load_extension(f'commands.{filename[:-3]}')
            return f"Loaded {filename}"
        except Exception as e:
            return f"Failed to load {filename}: {e}"

    async def load_extensions(self):
        extension_files = [filename for filename in os.listdir(
            './commands') if filename.endswith('.py')]
        workers = len(extension_files) + 1
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            results = await asyncio.gather(*[self.load_extension(filename) for filename in extension_files])

        end_time = time.time()
        elapsed_time = end_time - start_time
        for result in results:
            print(result)
        print(f"Elapsed time: {elapsed_time:.4f} seconds")

    @commands.command(
        name="reload",
        help="Reloads all bot commands",
        usage="reload"
    )
    async def reload_all(self, ctx):
        results = await self.load_extensions()
        for result in results:
            await ctx.send(result)


def setup(bot):
    bot.add_cog(Reload(bot))
