import discord
from discord.ext import commands
from discord import app_commands
from .voiceSynth_modal import voiceSynthModal

class AIvoice(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="AI TTS",
            callback=self.voiceSynth
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def voiceSynth(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("You need to be in a voice channel to use this command", ephemeral=True)
            return
        
        await interaction.response.send_modal(voiceSynthModal(user))


async def setup(bot):
    await bot.add_cog(AIvoice(bot))