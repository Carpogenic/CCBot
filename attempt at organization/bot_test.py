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

activity = discord.Activity(name='you', type=discord.ActivityType.watching)

bot = commands.Bot(command_prefix='.', intents=intents, activity=activity)
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

is_manual_stop = False

async def fetch_and_play(ctx, url, offset=0):
    global start_time, is_manual_stop
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
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
                after=lambda e: bot.loop.create_task(after_play(e, ctx)) if not is_manual_stop and ctx.voice_client else print("this is inside the after var")
            )
            last_played['url'] = url
            last_played['offset'] = int(offset)
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
   
        

# Define a simple View that gives us a confirmation menu
class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming', ephemeral=True)
        await interaction.message.delete()
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='No', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Starting at 0', ephemeral=True)
        await interaction.message.delete()
        self.value = False
        self.stop()


async def timecode_confirm_prompt(ctx: commands.Context):
    """Asks the user a question to confirm something."""
    # We create the view and assign it to a variable so we can wait for it later.
    view = Confirm()
    await ctx.send('Do you want to use the time in the URL as the start time?', view=view, delete_after=15)
    # Wait for the View to stop listening for input...
    await view.wait()
    if view.value is None:
        print('Timecode prompt timed out...')
        await ctx.send("Timed out: Starting song from the beginning")
    elif view.value:
        print('Timecode prompt confirmed...')
    else:
        print('Timecode prompt denied...')
    return view.value

async def get_timecode(ctx, url):
    pattern = r"\?t=(\d+)$"
    match = re.search(pattern, url)
    return int(match.group(1)) if match and await timecode_confirm_prompt(ctx) else 0


last_played = {"url": None, "offset": 0}
start_time = None
accumulated_time = 0


@bot.command()
async def play(ctx, url=None, providedOffset=None):
    global last_played, start_time, accumulated_time, is_manual_stop

    is_manual_stop = False

    if not url:
        if last_played and last_played['url'] and not ctx.voice_client.is_playing():
            offset = last_played['offset'] + accumulated_time
            await fetch_and_play(ctx, last_played['url'], offset)
        else:
            await ctx.send("No URL found to resume or queue, please provide a link.")
        return
    else:
        # New song is being provided
        if providedOffset:
            try:
                offset = int(providedOffset)
            except Exception as e:
                #i'll fix this some day
                user = None

                await ctx.message.add_reaction(bot.get_emoji(1083983552540053596))
                await ctx.send(f"Pretty sure '{providedOffset}' isn't a number, bro. -1 credit")
                return
        else:
            offset = await get_timecode(ctx, url)
        accumulated_time = 0
    # Check if the bot is either currently playing music or if there are songs queued up.
    if (ctx.voice_client and (ctx.voice_client.is_playing() or not song_queue.is_empty()) and url):
        song_queue.add(url, offset)
        await ctx.send(f"Song queued. Position: {len(song_queue._queue)}")
        print(song_queue._queue)
        return
    
    await fetch_and_play(ctx, url, offset)

    


@bot.command()
async def stop(ctx):
    global start_time, accumulated_time, last_played, is_manual_stop

    if ctx.voice_client and ctx.voice_client.is_playing():
        is_manual_stop = True
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