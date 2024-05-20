import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
TEST_GUILD = os.getenv('TEST_GUILD')
ELSIE = os.getenv('ELSIE')
DOOR = os.getenv('DOOR')
THEGAME_GUILD = os.getenv('THEGAME_GUILD')
scores_file = 'scores.json'

