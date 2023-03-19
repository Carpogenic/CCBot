import discord
from utils import update_scores


async def on_ready(bot):
    print(f'{bot.user.name} has connected to Discord!')


async def reaction_add_handler(bot, reaction, user, scores):
    message = reaction.message
    if message.author == bot.user:
        # The bot reacted to its own message
        return
    good_emoji = bot.get_emoji(1083983540124925952) # emoji ID
    if reaction.emoji == good_emoji:
        # Reacted with good emoji
        await message.add_reaction('👍')
        await update_scores(scores, message.author, user, 1)

    bad_emoji = bot.get_emoji(1083983552540053596)
    if reaction.emoji == bad_emoji:
        # Reacted with bad emoji
        await message.add_reaction('👎')
        await update_scores(scores, message.author, user, -1)