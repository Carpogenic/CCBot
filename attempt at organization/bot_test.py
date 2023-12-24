# todo: add cases for if reactions are removed

import os
import json
import discord
from discord.ext import commands
from config import token, GUILD, scores_file
import utils
import events
from commands.score import score_handler
import typing
import yt_dlp as yt_dlp
from functools import partial
import time
import re


intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.message_content = True
intents.presences = True
intents.guild_messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)
guild = discord.utils.get(bot.guilds, name=GUILD)

if os.path.exists(scores_file) and os.path.getsize(scores_file) > 0:
    with open(scores_file, 'r') as f:
        scores = json.load(f)
else:
    scores = {}


@bot.event
async def on_ready():
    utils.save_scores(scores)
    await events.on_ready(bot)

@bot.event
async def on_reaction_add(reaction, user):
    await events.reaction_add_handler(bot, reaction, user, scores)

@bot.command()
async def score(ctx, user: typing.Optional[discord.User] = None):
    await score_handler(ctx, bot, scores, user)

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

class Queue:
    def __init__(self):
        self._queue = []

    def add(self, url, offset=0):
        self._queue.append({
            "url": url,
            "offset": offset
        })

    def get_next(self):
        return self._queue.pop(0) if self._queue else None

    def is_empty(self):
        return not bool(self._queue)


song_queue = Queue()


def get_timecode(url):
    pattern = r"=(\d+)s$"
    match = re.search(pattern, url)
    return int(match.group(1)) if match else None

async def fetch_and_play(ctx, url, offset=0):
    global start_time
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        print(f"Only url:{url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']

            start_time = time.time()
            print("play triggered")
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(
                    executable="ffmpeg",
                    source=url2,
                    before_options=f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {offset}'
                ),
                after=lambda e: bot.loop.create_task(after_play(e, ctx))
            )
            last_played["url"] = url
    except Exception as e:
        await ctx.send(f"!!An error occurred: {e}")

async def play_next_song(ctx):
    print("play_next_song triggered")
    next_song = song_queue.get_next()
    if next_song:
        print(f"'from next_url'{next_song}")
        next_url = next_song["url"]
        next_offset = next_song["offset"]
        await fetch_and_play(ctx, next_url, next_offset)

async def after_play(error, ctx):
    print("after_play triggered")
    if error:
        print(f'Play error: {error}')
    await play_next_song(ctx)

last_played = {"url": None, "offset": 0}
start_time = None
accumulated_time = 0


@bot.command()
async def play(ctx, url=None, flag=None):
    global last_played, start_time, accumulated_time

    if not url:
        if last_played and last_played['url'] and not ctx.voice_client.is_playing():
            url = last_played['url']
            offset = last_played['offset'] + accumulated_time
        else:
            await ctx.send("No URL found to resume or queue, please provide a link.")
            return
    else:
        # New song is being provided
        offset = 0
        accumulated_time = 0

    # Check if the bot is either currently playing music or if there are songs queued up.
    if (ctx.voice_client and (ctx.voice_client.is_playing() or not song_queue.is_empty()) and url):
        song_queue.add(url)
        await ctx.send(f"Song queued. Position: {len(song_queue._queue)}")
        print(song_queue._queue)
        return

    
    await fetch_and_play(ctx, url, offset)

    


@bot.command()
async def stop(ctx):
    global start_time, accumulated_time, last_played

    if ctx.voice_client and ctx.voice_client.is_playing():
        # Calculate elapsed time from the last start_time and add to accumulated_time
        elapsed_time = time.time() - start_time
        accumulated_time += elapsed_time

        # Update the offset with accumulated_time
        last_played["offset"] += accumulated_time

        # Reset accumulated_time for next play
        accumulated_time = 0
        
        ctx.voice_client.stop()
        await ctx.send("Stopped the audio playback.")
    else:
        await ctx.send("I'm not currently playing anything.")



@bot.command()
async def skip(ctx):
    try:
        ctx.voice_client.stop()
        await play_next_song(ctx)
        await ctx.send("Skipped to the next song.")
    except Exception as e:
        await ctx.send(f"Error in skip: {e}")

help_text = """
**Bot Commands:**
`.join` - Makes the bot join the voice chat that you are in
`.leave.` - Makes the bot disconnect from voice chat
`.play <URL>` - Plays the song from the provided URL or resumes the last played song if no URL is given.
`.stop` - Stops the currently playing song.
`.skip` - Skips to the next song in the queue.
"""

@bot.command(name='halp')
async def help_command(ctx):
    await ctx.send(help_text)


""" file_path = "kaposis_sarkom.mp3"
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