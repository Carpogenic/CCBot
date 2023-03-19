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



bot.run(token)