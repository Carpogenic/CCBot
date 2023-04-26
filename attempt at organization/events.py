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
    good_emoji2 = bot.get_emoji(1100587677193080882) # jank
    if reaction.emoji in (good_emoji, good_emoji2):
        # Reacted with good emoji
        await message.add_reaction('👍')
        await update_scores(scores, message.author, user, 1)

    bad_emoji = bot.get_emoji(1083983552540053596)
    bad_emoji2 = bot.get_emoji(1100587719501029408)
    if reaction.emoji in (bad_emoji, bad_emoji2):
        # Reacted with bad emoji
        await message.add_reaction('👎')
        await update_scores(scores, message.author, user, -1)
