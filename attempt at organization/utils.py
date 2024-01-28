import json
import discord
from config import scores_file

def save_scores(scores):
    with open(scores_file, 'w') as f:
        json.dump(scores, f)
        
async def update_scores(ctx, scores, original_author, user, delta):
    # Update the score of the original_author in their guild by the delta value and save the updated scores
    original_author_id = str(original_author.id)
    guild_id = str(ctx.guild.id)
    if guild_id not in scores:
        scores[guild_id] = {}
    if original_author_id not in scores[guild_id]:
        scores[guild_id][original_author_id] = 0
    scores[guild_id][original_author_id] += delta
    save_scores(scores)

async def elsie_ellipsis_score(ELSIE, guild_id, scores, delta):
    original_author_id = str(ELSIE)
    guild_id = str(guild_id)
    if guild_id not in scores:
        scores[guild_id] = {}
    if original_author_id not in scores[guild_id]:
        scores[guild_id][original_author_id] = 0
    scores[guild_id][original_author_id] += delta
    save_scores(scores)
    