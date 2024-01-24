import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('DISCORD_BOT_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ELSIE = os.getenv('ELSIE')
scores_file = 'scores.json'

