# add queue list command to see what songs are queued

import os
import json
import discord
from discord.ext import commands
from config import token, GUILD, ELSIE
import utils
import events
from commands.score import score_handler
import typing
import yt_dlp as yt_dlp
from functools import partial
import time
import re
import asyncio
import random



intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.message_content = True
intents.presences = True
intents.guild_messages = True
intents.guilds = True
intents.members = True

# overwrite setup_hook to load cogs
class MyBot(commands.Bot):
    async def setup_hook(self) -> None:
        await utils.load_scores()

        print("Adding cogs")
        for root, _, files in os.walk('./cogs'):
            for filename in files:
                if filename.endswith("_cog.py"):
                    relative_path = os.path.relpath(root, './cogs')
                    dot_path = relative_path.replace(os.sep, '.')
                    extension_name = f'cogs.{dot_path}.{filename[:-3]}' if dot_path != '.' else f'cogs.{filename[:-3]}'
                    
                    try:
                        await self.load_extension(extension_name)
                        print(f"Loaded cog: {filename[:-7]}")
                    except Exception as e:
                        print(f"Failed to load cog {filename[:-7]}: {e}")
        return await super().setup_hook()



activity = discord.Activity(name='you', type=discord.ActivityType.watching)
bot = MyBot(command_prefix='.', intents=intents, activity=activity)
guild = discord.utils.get(bot.guilds, name=GUILD)



@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')



help_text = """
**Bot Commands:**
`.join` - Makes the bot join the voice chat that you are in
`.leave.` - Makes the bot disconnect from voice chat
`.play <URL>` - Plays the song from the provided URL or resumes the last played song if no URL is given.
`.stop` - Stops the currently playing song.
`.skip` - Skips to the next song in the queue.
`.queue, .q` - Displays the queue.
"""

@bot.command(name='halp')
async def help_command(ctx):
    await ctx.send(help_text)


""" file_path = "path/to/file"
@bot.command()
async def play_file(ctx):
    # Check if the bot is connected to a voice channel
    if bot.voice_clients:
        voice_client = bot.voice_clients[0]  # Get the first voice client

        # Play the local file if not already playing
        if not voice_client.is_playing():
            audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=file_path)
            voice_client.play(audio_source)
        else:
            await ctx.send("Already playing audio.")
    else:
        await ctx.send("Bot is not connected to any voice channel.") """



bot.run(token)