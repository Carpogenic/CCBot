import discord 
from discord.ext import commands

class Queue:
    def __init__(self):
        self._queue = []
        self.current_song = None

    def set_current(self, song):
        self.current_song = song

    def add(self, url, offset=0, song_title=None):
        self._queue.append({
            "url": url,
            "offset": offset,
            "title": song_title
        })

    def get_next(self):
        if self._queue:
            next_song = self._queue.pop(0)
            self.current_song = next_song['title']
            return next_song
        return None
    
    def is_empty(self):
            return not bool(self._queue)
    
    def clear(self):
        self._queue = []


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

    @discord.ui.button(label='No', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Starting at 0', ephemeral=True)
        await interaction.message.delete()
        self.value = False
        self.stop()
