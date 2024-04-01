#todo: move stop logic to MusicPlayer so play_local_sound doesn't disregard elapsed_time

import discord
from discord.ext import commands
from .music_player import MusicPlayer
from .music_utils import LocalSoundsView
import time


is_manual_stop = False

class musicCog(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.player = MusicPlayer(bot)


    @commands.command()
    async def join(self, ctx):
        await self.player.join(ctx)

    @commands.command()
    async def leave(self, ctx):
        self.player.clear_queue()
        self.player.last_played = None
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, url=None, providedOffset=None):

        self.player.is_manual_stop = False
        
        if not ctx.voice_client:
            await self.join(ctx)

        if not url:
            if self.player.last_played and self.player.last_played['url'] and not ctx.voice_client.is_playing():
                offset = self.player.last_played['offset'] + self.player.accumulated_time
                await self.player.fetch_and_play(ctx, self.player.last_played['url'], offset)
            else:
                await ctx.send("No URL found to resume or queue, please provide a link.")
            return
        else:
            # New song is being provided
            if providedOffset:
                try:
                    offset = int(providedOffset)
                except Exception as e:

                    await ctx.message.add_reaction(self.bot.get_emoji(1083983552540053596))
                    await ctx.send(f"Pretty sure '{providedOffset}' isn't a number, bro. -1 credit")
                    return
            else:
                offset = await self.player.get_timecode(ctx, url)
            self.player.accumulated_time = 0
        # Check if the bot is either currently playing music or if there are songs queued up.
        if (ctx.voice_client and (ctx.voice_client.is_playing() or not self.player.song_queue.is_empty()) and url):
            song_title = await self.player.get_song_title(url)
            self.player.song_queue.add(url, offset, song_title)
            await ctx.send(f"Song queued. Position: {len(self.player.song_queue._queue)}")
            print(self.player.song_queue._queue)
            return
        self.player.song_queue.set_current(await self.player.get_song_title(url))
        await self.player.fetch_and_play(ctx, url, offset)
    
    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            try:
                self.player.is_manual_stop = True
                # Calculate elapsed time from the last start_time and add to accumulated_time
                elapsed_time = time.time() - self.player.start_time
                self.player.accumulated_time += elapsed_time

                # Update the offset with accumulated_time
                self.player.last_played["offset"] += self.player.accumulated_time

                # Reset accumulated_time for next play
                self.player.accumulated_time = 0
            except:
                pass
            finally:
                ctx.voice_client.stop()
                await ctx.send("Stopped the audio playback.")
        else:
            await ctx.send("I'm not currently playing anything.")

    @commands.command()
    async def skip(self, ctx):
        try:
            ctx.voice_client.stop()
            await ctx.send("Skipped to the next song.")
        except Exception as e:
            await ctx.send(f"Error in skip: {e}")

    @commands.command(aliases=['q', 'queue'])
    async def display_queue(self, ctx):
        message_parts = []

        # Include the currently playing song if there is one
        if self.player.song_queue.current_song:
            message_parts.append(f"**Currently playing:** {self.player.song_queue.current_song}")

        # Add the upcoming songs in the queue
        if not self.player.song_queue.is_empty():
            title_list = '\n'.join(f'{idx + 1}. {song["title"]}' for idx, song in enumerate(self.player.song_queue._queue))
            message_parts.append(f"**Upcoming:**\n{title_list}")
        elif not message_parts:
            message_parts.append("The song queue is currently empty.")

        message = '\n\n'.join(message_parts)
        await ctx.send(message)

    @commands.hybrid_command(name="play_file", description="Play a local sound file")
    async def play_local(self, ctx):
        directory = "./sounds"

        if not ctx.voice_client:
            await self.join(ctx)

        await ctx.send("Select a sound:", view=LocalSoundsView(directory, self.player), delete_after=850)
    



async def setup(bot):
    await bot.add_cog(musicCog(bot))