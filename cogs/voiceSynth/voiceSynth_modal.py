import discord
from .voiceSynth_assisstant import generate_voice_response
class voiceSynthModal(discord.ui.Modal):
    def __init__(self, user: discord.User):
        super().__init__(title="Generate voice prompt (optional)")
        self.prompt = discord.ui.TextInput(
            label="Prompt",  # Added label here
            style=discord.TextStyle.long,
            placeholder="Text goes here",
            required=False,
            max_length=400
        )
        self.add_item(self.prompt)
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        prompt = "Sender: " + interaction.user.display_name + "\n" + "Recipient: " + self.user.display_name + "\n" + "Prompt: " + self.prompt.value
        await interaction.response.send_message(await generate_voice_response(prompt))
        