import discord
from discord.ext import commands
import yt_dlp as yt_dlp
import time
import re
import os
from .music_utils import Queue, Confirm
import traceback



class MusicPlayer:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.song_queue = Queue()
        self.last_played = {"url": None, "offset": 0}
        self.start_time = None
        self.accumulated_time = 0
        self.is_manual_stop = False

    async def join(self, ctx):
        await ctx.author.voice.channel.connect()

    async def fetch_and_play(self, ctx, url, offset=0):
        print(f"this is the printing of the queue this time{self.song_queue._queue}")
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

                self.start_time = time.time()
                print("play triggered")
                ctx.voice_client.play(
                    discord.FFmpegPCMAudio(
                        executable="ffmpeg",
                        source=url2,
                        before_options=f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {offset}'
                    ),
                    after=lambda e: self.bot.loop.create_task(self.after_play(e, ctx)) if not self.is_manual_stop and ctx.voice_client else None
                )
                self.last_played['url'] = url
                self.last_played['offset'] = int(offset)
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f"!!An error occurred: {e}")

    async def play_next_song(self, ctx):
        print("play_next_song triggered")
        next_song = self.song_queue.get_next()
        if next_song:
            print(f"'from next_url'{next_song}")
            next_url = next_song["url"]
            next_offset = next_song["offset"]
            await self.fetch_and_play(ctx, next_url, next_offset)

    async def after_play(self, error, ctx):
        print("after_play triggered")
        if error:
            print(f'Play error: {error}')
        await self.play_next_song(ctx)

    def clear_queue(self):
        self.song_queue.clear()

    async def get_timecode(self, ctx, url):
        pattern = r"\?t=(\d+)$"
        match = re.search(pattern, url)
        return int(match.group(1)) if match and await self.timecode_confirm_prompt(ctx) else 0

    async def get_song_title(self, url: str) -> str:
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title', 'Title not found')
        except Exception as e:
            return f"An error occurred: {e}"


    async def timecode_confirm_prompt(self, ctx: commands.Context):
        """Asks the user a question to confirm something."""
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



    # for playing local sounds


    async def play_local_sound(self, interaction: discord.Interaction, file_path: str):
        # Play the local file if not already playing
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
        try:
            audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=file_path)
            interaction.guild.voice_client.play(audio_source)
        except Exception as e:
            print(f"Play Local Sound error: {e}")
