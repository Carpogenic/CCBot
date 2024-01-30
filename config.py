import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEST_GUILD = os.getenv('TEST_GUILD')
ELSIE = os.getenv('ELSIE')
scores_file = 'scores.json'

