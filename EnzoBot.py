import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime
from constants import *

load_dotenv('token.env')
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
enzoBot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)

utc = datetime.timezone.utc
time = datetime.time(hour=3, minute=0, tzinfo=utc)


class MessageUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_task.start()

    def cog_unload(self):
        self.my_task.cancel()

    @tasks.loop(time=time)
    async def my_task(self):
        await updateMessage()


def generateUpdatedContent(content: str):
    splitContent = content.split()
    updatedDays = int(splitContent[INDEX_DAYS].replace('*', '')) + 1
    splitContent[INDEX_DAYS] = f"**{updatedDays}**"
    splitContent[INDEX_NEW_LINE] += "\n\n"
    return f"{' '.join(splitContent[:SPLIT])}{' '.join(splitContent[SPLIT:])}"


async def resetExistingMessage(message):
    await message.edit(content=INITIAL_MESSAGE)


async def sendInitialMessage(channel):
    await channel.send(content=INITIAL_MESSAGE, file=discord.File(IMAGE_PATH))


async def getLastMessage(channel):
    try:
        return [message async for message in channel.history(limit=1)][0]
    except IndexError:
        return None


async def updateMessage():
    channel = enzoBot.get_channel(CHANNEL_ID)
    message = await getLastMessage(channel)
    if message and message.author.id == ENZO_BOT_ID:
        updatedContent = generateUpdatedContent(message.content)
        await message.edit(content=updatedContent)


async def resetMessage():
    channel = enzoBot.get_channel(CHANNEL_ID)
    message = await getLastMessage(channel)
    if message and message.author.id == ENZO_BOT_ID:
        await resetExistingMessage(message)
    else:
        await sendInitialMessage(channel)


@enzoBot.command(name="sumar")
async def sumar(ctx):
    await updateMessage()


@enzoBot.command(name="reiniciar")
async def reiniciar(ctx):
    await resetMessage()


@enzoBot.event
async def on_ready():
    await enzoBot.change_presence(activity=discord.Game(name="el Pepe"))
    MessageUpdater(enzoBot)


@enzoBot.event
async def on_message(message: discord.Message):
    if message.channel.id == CHANNEL_ID and message.author.id != ENZO_BOT_ID:
        await message.delete()
    await enzoBot.process_commands(message)


enzoBot.run(TOKEN)
