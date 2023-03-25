import os

from discord import Message
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
        """
        Updates the message once a day.
        """
        await updateMessage()


def generateUpdatedContent(content: str) -> str:
    """
    :param content: Content from a discord.Message. It must have INITIAL_MESSAGE format i.e. it's the message from
    CHANNEL_ID that Enzo sent, containing the day counter.
    :return: Returns a newly generated text, with correct format and updated day counter.
    TODO: This implementation works but it's highly error prone. It's basically text hardcoding. The day counter should
        be extracted and maybe saved in a file. As is, it doesn't depend on the bot's uptime, but the updating does.
    """
    splitContent = content.split()
    updatedDays = int(splitContent[INDEX_DAYS].replace('*', '')) + 1
    splitContent[INDEX_DAYS] = f"**{updatedDays}**"
    splitContent[INDEX_NEW_LINE] += "\n\n"
    return f"{' '.join(splitContent[:SPLIT])}{' '.join(splitContent[SPLIT:])}"


async def resetExistingMessage(message: discord.Message) -> None:
    """
    :param message: Message must be sent by Enzo (message.id must be ENZO_BOT_ID)
    Modifies message content with INITIAL_MESSAGE.
    """
    await message.edit(content=INITIAL_MESSAGE)


async def sendInitialMessage(channel: discord.TextChannel) -> None:
    """
    Sends INITIAL_MESSAGE with IMAGE_PATH file to the desired channel, usually to CHANNEL_ID channel.
    """
    await channel.send(content=INITIAL_MESSAGE, file=discord.File(IMAGE_PATH))


async def getLastMessage(channel: discord.TextChannel) -> Message | None:
    """
    :return: Returns the last message from the desired channel. Returns None if it doesn't exist.
    """
    try:
        return [message async for message in channel.history(limit=1)][0]
    except IndexError:
        return None


async def updateMessage() -> None:
    """
    Adds one to the day counter.
    TODO: Consider the case where the message doesn't exist or the last one isn't from Enzo's ID.
    """
    channel = enzoBot.get_channel(CHANNEL_ID)
    message = await getLastMessage(channel)
    if message and message.author.id == ENZO_BOT_ID:
        updatedContent = generateUpdatedContent(message.content)
        await message.edit(content=updatedContent)


async def resetMessage() -> None:
    """
    Resets the message to INITIAL_MESSAGE by modifying it. If it doesn't exist or the last one isn't from Enzo's ID,
    sends a new one.
    """
    channel = enzoBot.get_channel(CHANNEL_ID)
    message = await getLastMessage(channel)
    if message and message.author.id == ENZO_BOT_ID:
        await resetExistingMessage(message)
    else:
        await sendInitialMessage(channel)


def isEnzoMentioned(content: str) -> bool:
    """
    :param content: Content from a discord.Message.
    :return: True if the content contains keyword "enzo", ignoring uppercase characters. False otherwise.
    """
    return False if content.lower().find("enzo") == -1 else True


@enzoBot.command(name="sumar")
async def sumar(ctx) -> None:
    """
    :param ctx: discord.Message context, unused.
    Adds one to the day counter.
    """
    await updateMessage()


@enzoBot.command(name="reiniciar")
async def reiniciar(ctx) -> None:
    """
    :param ctx: discord.Message context, unused.
    Resets the message to INITIAL_MESSAGE.
    """
    await resetMessage()


@enzoBot.event
async def on_ready() -> None:
    """
    Changes activity and initializes the MessageUpdater Cog.
    """
    await enzoBot.change_presence(activity=discord.Game(name="el Pepe"))
    MessageUpdater(enzoBot)


@enzoBot.event
async def on_message(message: discord.Message) -> None:
    """
    Executes different actions based on channnel and user ID.
    TODO: Separate the different cases for better expandability.
    """
    if message.channel.id == CHANNEL_ID and message.author.id != ENZO_BOT_ID:
        await message.delete()
    elif message.channel.id != CHANNEL_ID and isEnzoMentioned(message.content):
        await message.channel.send(content="Yo")
    await enzoBot.process_commands(message)


enzoBot.run(TOKEN)
