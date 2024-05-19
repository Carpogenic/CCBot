import discord
from discord.ext import commands
from discord import app_commands
from .voiceSynth_modal import voiceSynthModal

class AIvoice(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Test",
            callback=self.contestmenu
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def contestmenu(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_modal(voiceSynthModal(user))


async def setup(bot):
    await bot.add_cog(AIvoice(bot))