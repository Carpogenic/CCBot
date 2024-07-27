# add descriptions to commands and remove the jank .halp command
# remove traceback from music_player as soon as i figure out what the random error is
# generalize elsie_ellipsis_score in utils so that voiceSynth_play can actually remove credits

# voiceSynth: move check for if user is in a voice channel from _play to _cog  /- added a check to cog but _play still has some unecessary stuff
# also add check for if user is in a different channel from bot in _cog

import os
import discord
from discord.ext import commands
from config import TOKEN, TEST_GUILD
import utils
from discord import app_commands



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
                    print(f"\n{extension_name}")

                    try:
                        await self.load_extension(extension_name)
                        print(f"Loaded cog: {filename[:-7]}")
                    except Exception as e:
                        print(f"Failed to load cog {filename[:-7]}: {e}")



        return await super().setup_hook()



activity = discord.Activity(name='you', type=discord.ActivityType.watching)
bot = MyBot(command_prefix='.', intents=intents, activity=activity)



@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.tree.command(name="echo", description="Echoes a message.")
@app_commands.describe(message="The message to echo.")
async def echo(interaction: discord.Interaction, message: str) -> None:
    await interaction.response.send_message(message)
    """ await interaction.followup.send("This is a followup message.")
    await interaction.followup.send("This is another followup message.") """

# Reloads a specified cog. If no extension is provided, it reloads the last used cog.
currentWorkingCog = None
@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension: str = None):
    global currentWorkingCog

    extension = extension or currentWorkingCog
    currentWorkingCog = extension

    if extension is None:
        await ctx.send("No extension specified and no previous extension to reload.")
        return
    # try reloading the cog
    try:
        await bot.reload_extension(f"{extension}")
        await ctx.send(f"Reloaded: {extension}")
    except commands.ExtensionNotLoaded:
        # try loading the cog if not already loaded
        try:
            await bot.load_extension(f"{extension}")
            await ctx.send(f"Loaded: {extension}")
        except Exception as e:
            await ctx.send(f"Error: {e}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# syncs app commands with discord
@bot.command(hidden=True)
@commands.is_owner()
async def sync(ctx, target):
    if target == "all":
        await bot.tree.sync()
        print("Synced all")
        await ctx.send("Synced all")

    elif target == "test":
        bot.tree.copy_global_to(guild=discord.Object(id=TEST_GUILD))
        await bot.tree.sync(guild=discord.Object(id=TEST_GUILD))
        print("Synced test")
        await ctx.send("Synced Test")

    else:
        await ctx.send("Invalid target. Use 'all' or 'test'.")





help_text = """
**Bot Commands:**
`.join` - Makes the bot join the voice chat that you are in
`.leave.` - Makes the bot disconnect from voice chat
`.play <URL>` - Plays the song from the provided URL or resumes the last played song if no URL is given.
`.play_file` or `/play_file` - Plays a local sound file, doesn't respect the queue.
`.stop` - Stops the currently playing song.
`.skip` - Skips to the next song in the queue.
`.queue, .q` - Displays the queue.
`/poll` - Create a poll that people can vote in.
"""

@bot.command(name='halp')
async def help_command(ctx):
    await ctx.send(help_text)


bot.run(TOKEN)
