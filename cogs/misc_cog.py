from discord.ext import commands
import utils
import asyncio
import random
from config import ELSIE


class miscCog(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == int(ELSIE) and message.content == "...":
            await utils.elsie_ellipsis_score(ELSIE, message.guild.id, 1)
            await asyncio.sleep(random.randint(1, 10))
            await message.channel.send("...")

async def setup(bot):
    await bot.add_cog(miscCog(bot))