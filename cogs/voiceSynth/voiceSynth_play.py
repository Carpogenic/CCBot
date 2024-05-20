import subprocess
import discord
import asyncio
import tempfile
import os

async def play_audio(interaction: discord.Interaction, audio_stream):
    # Get the voice state of the user who invoked the command
    user_voice_state = interaction.user.voice
    if user_voice_state is None or user_voice_state.channel is None:
        await interaction.followup.send("You need to be in a voice channel to use this command.", ephemeral=True)
        return

    # Connect to the user's voice channel if not already connected
    voice_channel = user_voice_state.channel
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        # Bot is not connected to any voice channel, so connect to the user's channel
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        # Bot is connected to a different channel, so inform the user
        await interaction.followup.send(f"The bot is already in another voice channel: {voice_client.channel.name}.", ephemeral=True)
        return

    # Write audio stream to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_file.write(audio_stream)
        temp_audio_file_path = temp_audio_file.name

    # Play the audio using discord.FFmpegOpusAudio
    audio_source = discord.FFmpegOpusAudio(temp_audio_file_path)
    voice_client.play(audio_source)

    await interaction.followup.send("Voice synthesis complete and playing in the channel.", ephemeral=True)

    # Ensure to delete the temporary file after playback
    while voice_client.is_playing():
        await asyncio.sleep(1)
    os.remove(temp_audio_file_path)
