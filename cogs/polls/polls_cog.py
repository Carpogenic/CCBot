import discord
from discord import app_commands
from discord.ext import commands

from .poll_modal import pollModal

class pollsCog(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command(name="poll", description="Make a poll and get people to vote.")
    @app_commands.describe(options="Roughly how many options you think you'll need")
    @app_commands.choices(options=[
        app_commands.Choice(name="Two", value=2),
        app_commands.Choice(name="Three", value=3),
        app_commands.Choice(name="Five", value=5)
    ])
    async def create_poll(self, interaction: discord.Interaction, options: int):
        author = interaction.user
        await interaction.response.send_modal(pollModal(author, options))


async def setup(bot):
    await bot.add_cog(pollsCog(bot))
