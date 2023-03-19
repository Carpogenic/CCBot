import discord
import random
import typing 

# shows all scores or score of a user if specified
async def score_handler(ctx, bot, scores, user: typing.Optional[discord.User] = None):
    guild = ctx.message.guild
    if user is None:
        # Show the entire scoreboard
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        scoreboard = []
        for user_id, score in sorted_scores:
            member = guild.get_member(int(user_id))
            if member:
                name = member.nick or member.name
            else:
                user = await bot.fetch_user(user_id)
                name = user.name
            scoreboard.append(f'{name}: {score} credits')
        await ctx.send('\n'.join(scoreboard))


    else:
        user_id = str(user.id)
        score = scores.get(user_id, 0)
        if score > 0:
            messages = [f'{user.display_name} has {score} credits.',
                        f'{user.display_name} is still okay with {score} credits.',
                        f'{user.display_name} making us proud, {score} credits.']
            message = random.choice(messages)
            await ctx.send(message)
        elif score == 0:
            messages = [f'{user.display_name} has literally {score} credits. Keep it up, I guess.', 
                        f'{user.display_name} has zero credits.',
                        f'Zero credits, what a joke']
            message = random.choice(messages)
            await ctx.send(message)
        else:
            messages = [f'{user.display_name} has {score} credits. Good luck in the future ;)', 
                        f'{user.display_name} needs to step up their game very soon with {score} credits.',
                        f'{user.display_name} has {score} credits, we\'re on our way',
                        f'{score} credits... Are they there yet, {user.display_name}?']
            message = random.choice(messages)
            await ctx.send(message)
