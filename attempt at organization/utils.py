import json
from config import scores_file

def save_scores(scores):
    with open(scores_file, 'w') as f:
        json.dump(scores, f)
        
async def update_scores(scores, original_author, user, delta):
    original_author_id = str(original_author.id)
    if original_author_id not in scores:
        scores[original_author_id] = 0
    scores[original_author_id] += delta
    save_scores(scores)