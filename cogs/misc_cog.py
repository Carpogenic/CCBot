from discord.ext import commands
import utils
import asyncio
import random
from config import ELSIE, THEGAME_GUILD, DOOR


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

    @commands.command(aliases=['d', 'door', 'code', 'c', 'doorcode'], hidden=True)
    async def doorcode_reminder(self, ctx):
        if ctx.guild.id == int(THEGAME_GUILD):
            await ctx.send(DOOR)
        else:
            return
        
        

async def setup(bot):
    await bot.add_cog(miscCog(bot))