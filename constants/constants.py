from os import getenv
from dotenv import load_dotenv

load_dotenv('tokens.env')
TOKEN = getenv('TOKEN')
ORURA_ID = int(getenv('ORURA_ID'))
ENZO_BOT_ID = int(getenv('ENZO_BOT_ID'))
CHANNEL_ID = int(getenv('CHANNEL_ID'))

# MOVE

INITIAL_MESSAGE = f'El "Dia del Accidente" es cuando a <@{ORURA_ID}> le da o se pelea con alguien y ' \
                  'semi-borra usuarios del server porque esta enojada/triste/retrasada mental.\n\nActualmente ' \
                  'pasaron **0** día(s) desde el último accidente.'

MESSAGE_FIRST_HALF = f'El "Dia del Accidente" es cuando a <@{ORURA_ID}> le da o se pelea con alguien y ' \
                     'semi-borra usuarios del server porque esta enojada/triste/retrasada mental.\n\nActualmente ' \
                     'pasaron **'

MESSAGE_SECOND_HALF = f"** día(s) desde el último accidente."

SIRIUS_IMAGE_PATH = "images/sirius_black.png"
DAY_COUNTER_BINARY_PATH = "binary/counterInfo.dat"

SEARCH_LIMIT = 1
ERROR = -1

SECONDS_IN_DAY = 86400
TIMEZONE = -10800

DAYS = 0

MAX_TIME = [23, 59, 59]
TIME_IN_SECONDS = [3600, 60, 1]
