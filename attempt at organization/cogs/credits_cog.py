from discord.ext import commands
import events
import typing 
import discord
from commands.score import score_handler

class credits(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

    # add or remove points from a user if their message is reacted to with the proper emoji
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await events.reaction_add_handler(self.bot, reaction)

    @commands.command(aliases=["scores"])
    async def score(self, ctx, user: typing.Optional[discord.User] = None):
        await score_handler(ctx, self.bot, user)

async def setup(bot):
    await bot.add_cog(credits(bot))