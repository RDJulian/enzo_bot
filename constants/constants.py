from os import getenv
from dotenv import load_dotenv

load_dotenv('tokens.env')
TOKEN = getenv('TOKEN')
ORURA_ID = int(getenv('ORURA_ID'))
ENZO_BOT_ID = int(getenv('ENZO_BOT_ID'))
RESERVED_CHANNEL_ID = int(getenv('CHANNEL_ID'))
