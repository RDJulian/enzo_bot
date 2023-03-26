import datetime
import time
from os import path
import pickle
import discord
from discord.ext import tasks, commands
from constants import *


async def getFirstEnzoMessage(channel: discord.TextChannel) -> discord.Message | None:
    message = await anext(channel.history(limit=1, oldest_first=True), None)
    return message if message and message.author.id == ENZO_BOT_ID else None


async def sendInitialMessage(channel: discord.TextChannel) -> None:
    """
    Sends INITIAL_MESSAGE with IMAGE_PATH file to the desired channel, usually to CHANNEL_ID channel.
    """
    await channel.send(content=INITIAL_MESSAGE, file=discord.File(IMAGE_PATH))


async def resetExistingMessage(message: discord.Message) -> None:
    """
    :param message: Must be sent by Enzo (message.id must be ENZO_BOT_ID).
    Modifies message content with INITIAL_MESSAGE.
    """
    await message.edit(content=INITIAL_MESSAGE)


async def purgeChannel(channel: discord.TextChannel):
    await channel.purge()


def generateUpdatedContent(days: int) -> str:
    """
    Returns a newly generated text, with correct format and updated day counter.
    """
    return f"{MESSAGE_FIRST_HALF}{days}{MESSAGE_SECOND_HALF}"


def saveToBinaryFile(filePath: str, resetTime: float) -> None:
    with open(filePath, "wb") as file:
        pickle.dump(resetTime, file)


class MessageUpdater(commands.Cog):
    def __init__(self, bot: commands.Bot, unixTime: float):
        self.bot = bot
        self.unixTime = unixTime
        self.resetTime = datetime.datetime.fromtimestamp(unixTime).time()
        self.loop = self.loadLoop(self.resetTime).start()
        self.dayCounter = int(time.time() - unixTime / 86400)

    def updateLoopTime(self, resetTime):
        """
        Updates loop time by unloading old loop and reloading a new one with the desired time.
        """
        self.loop.cancel()
        self.loop = self.loadLoop(resetTime).start()

    def loadLoop(self, resetTime) -> callable:
        """
        Returns loop task with the desired time.
        """

        @tasks.loop(time=resetTime)
        async def updateMessage():
            """
            Updates the day counting message, adding one to the counter. If it doesn't exist or last message isn't from
            Enzo, generates a new one.
            TODO: Inject dependency by passing channel ID. That way, it could work on any channel.
            """
            channel = self.bot.get_channel(CHANNEL_ID)
            message = await getFirstEnzoMessage(channel)
            self.dayCounter += 1
            updatedContent = generateUpdatedContent(self.dayCounter)
            if message and message.author.id == ENZO_BOT_ID:
                await message.edit(content=updatedContent)
            else:
                await channel.send(content=updatedContent, file=discord.File(IMAGE_PATH))

        return updateMessage

    @commands.command(name="reiniciar")
    async def resetMessage(self, ctx) -> None:
        """
        :param ctx: discord.Message context, unused.
        Resets the message to INITIAL_MESSAGE by modifying it. If it doesn't exist or the last one isn't from Enzo's ID,
        sends a new one.
        """
        channel = self.bot.get_channel(CHANNEL_ID)
        message = await getFirstEnzoMessage(channel)
        if message and message.author.id == ENZO_BOT_ID:
            await resetExistingMessage(message)
        else:
            await purgeChannel(channel)
            await sendInitialMessage(channel)
        # CAMBIAR
        self.dayCounter = 0
        self.updateLoopTime(datetime.datetime.utcfromtimestamp(unixTime := (time.time() - 86400 * 8)).time())
        self.unixTime = unixTime
        saveToBinaryFile(BINARY_FILE_PATH, unixTime)

    @commands.command(name="actualizar")
    async def updateMessage(self, ctx) -> None:
        channel = self.bot.get_channel(CHANNEL_ID)
        message = await getFirstEnzoMessage(channel)
        self.dayCounter = int((time.time() - self.unixTime) / 86400)
        updatedContent = generateUpdatedContent(self.dayCounter)
        if message and message.author.id == ENZO_BOT_ID:
            await message.edit(content=updatedContent)
        else:
            await channel.send(content=updatedContent, file=discord.File(IMAGE_PATH))


def readBinaryFile(filePath: str) -> float:
    if path.isfile(filePath):
        with open(filePath, "rb") as file:
            resetTime = pickle.load(file)
        return resetTime
    else:
        resetTime = time.time()
        saveToBinaryFile(filePath, resetTime)
        return resetTime


async def setup(bot: commands.Bot):
    """
    Initializes and adds Cog to Bot.
    """
    resetTime = readBinaryFile(BINARY_FILE_PATH)
    await bot.add_cog(MessageUpdater(bot, resetTime))
