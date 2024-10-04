# each user gets their own convo but can respond to the latest one active
# unless they have their own active convo
# there is a cooldown until the convo isn't considered active any more


import discord
from discord.ext import commands
from .ollama_chat import ollamaHandler

class ollamaCog(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.convo = ollamaHandler(bot)
    

    @commands.command(aliases=["clear"])
    async def clear_chat(self, ctx):
        await self.convo.clear(ctx)
    
    @commands.command(aliases=["ch", "talk"])
    async def respond(self, ctx, *, prompt):
        await self.convo.user_message(ctx, prompt)

async def setup(bot):
    await bot.add_cog(ollamaCog(bot))