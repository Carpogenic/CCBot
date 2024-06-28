import discord
from .voiceSynth_generate import generate_response, get_audio_stream
from .voiceSynth_play import play_audio

class voiceSynthModal(discord.ui.Modal):
    def __init__(self, user: discord.User):
        super().__init__(title="Generate voice prompt")
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
        await interaction.response.defer(ephemeral=True)  # Defer the interaction response to keep it active

        
        prompt = "Sender: " + interaction.user.display_name + "\n" + "Recipient: " + self.user.display_name + "\n" + "Prompt: " + self.prompt.value
        response_json = await generate_response(prompt)
        if response_json:
            language = response_json.get("language", "English")  # Default to English if not specified
            gender = response_json.get("gender", "Male")  # Default to Male if not specified
            response_text = response_json.get("response", "")
            audio_stream = await get_audio_stream(response_text, language, gender)
            if audio_stream:
                await play_audio(interaction, audio_stream)
        else:
            await interaction.followup.send("Failed to generate voice response.", ephemeral=True)





        #await interaction.followup.send(await generate_response(prompt))
        