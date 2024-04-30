import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEST_GUILD = os.getenv('TEST_GUILD')
ELSIE = os.getenv('ELSIE')
DOOR = os.getenv('DOOR')
THEGAME_GUILD = os.getenv('THEGAME_GUILD')
scores_file = 'scores.json'

