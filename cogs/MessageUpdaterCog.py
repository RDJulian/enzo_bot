import datetime
import time
import discord
from discord.ext import tasks, commands
from binaryFileHandler import loadBinaryFile, saveToBinaryFile
from constants import *


def isValidDayInput(days: str) -> bool:
    """
    Returns True if the input text is valid i.e. can be cast to int and greater or equal to zero. False otherwise.
    """
    try:
        days = int(days)
        return days >= 0
    except ValueError:
        return False


async def getFirstEnzoMessage(channel: discord.TextChannel) -> discord.Message | None:
    """
    Returns the first message from the desired channel if it is from Enzo. Otherwise, returns None.
    """
    message = await anext(channel.history(limit=SEARCH_LIMIT, oldest_first=True), None)
    return message if message and message.author.id == ENZO_BOT_ID else None


def generateUpdatedContent(days: int) -> str:
    """
    Returns a newly generated text, with correct format and updated day counter.
    """
    return f"{MESSAGE_FIRST_HALF}{days}{MESSAGE_SECOND_HALF}"


def convertUnixToTime(unixTime: int) -> datetime.time:
    """
    Converts unixTime to time object i.e. without date and returns it.
    """
    return datetime.datetime.fromtimestamp(unixTime).time()


def getDayCounter(unixTime: int) -> int:
    """
    Calculates difference between current and saved time, rounded in days, and returns it.
    """
    return int((time.time() - unixTime) / SECONDS_IN_DAY)


class MessageUpdater(commands.Cog):
    def __init__(self, bot: commands.Bot, unixTime: int) -> None:
        self.bot = bot
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime + TIMEZONE)).start()

    def updateLoopTime(self, unixTime: int) -> None:
        """
        Updates loop time by unloading old loop and reloading a new one with the desired Unix time, then saves it.
        """
        self.loop.cancel()
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime + TIMEZONE)).start()
        saveToBinaryFile(BINARY_FILE_PATH, unixTime)

    def loadLoop(self, loopTime: datetime.time) -> callable:
        """
        Returns loop task with the desired time.
        """

        @tasks.loop(time=loopTime)
        async def updateMessage() -> None:
            """
            Updates the day counting message, adding one to the counter. If it doesn't exist or last message isn't from
            Enzo, wipes channel and generates a new one.
            TODO: Inject dependency by passing channel ID. That way, it could work on any channel.
            """
            channel = self.bot.get_channel(CHANNEL_ID)
            message = await getFirstEnzoMessage(channel)
            updatedContent = generateUpdatedContent(getDayCounter(self.unixTime))
            if message and message.author.id == ENZO_BOT_ID:
                await message.edit(content=updatedContent)
            else:
                await channel.purge()
                await channel.send(content=updatedContent, file=discord.File(IMAGE_PATH))

        return updateMessage

    @commands.command(name="reiniciar")
    async def resetMessage(self, context: commands.Context) -> None:
        """
        :param context: unused.
        Resets the message to INITIAL_MESSAGE by modifying it. If it doesn't exist or the last one isn't from Enzo's ID,
        wipes channel and sends a new one.
        """
        channel = self.bot.get_channel(CHANNEL_ID)
        message = await getFirstEnzoMessage(channel)
        if message and message.author.id == ENZO_BOT_ID:
            await message.edit(content=INITIAL_MESSAGE)
        else:
            await channel.purge()
            await channel.send(content=INITIAL_MESSAGE, file=discord.File(IMAGE_PATH))
        self.updateLoopTime(int(time.time()))

    @commands.command(name="refrescar")
    async def refreshMessage(self, context: commands.Context) -> None:
        """
        :param context: unused.
        Refreshes the message by modifying it. It's content may not change. If it doesn't exist or the last one isn't
        from Enzo's ID, wipes channel and sends a new one.
        """
        channel = self.bot.get_channel(CHANNEL_ID)
        message = await getFirstEnzoMessage(channel)
        updatedContent = generateUpdatedContent(getDayCounter(self.unixTime))
        if message and message.author.id == ENZO_BOT_ID:
            await message.edit(content=updatedContent)
        else:
            await channel.purge()
            await channel.send(content=updatedContent, file=discord.File(IMAGE_PATH))

    @commands.command(name="modificar")
    async def modifyMessage(self, context: commands.Context, *args: str) -> None:
        """
        :param args: days: str. Castable to int and greater or equal to zero only.
        :param context: unused.
        Modifies the message with the desired day counter by modifying it. If it doesn't exist or the last one isn't
        from Enzo's ID, wipes channel and sends a new one. Meant as a debug command.
        """

        if len(args) == 1 and isValidDayInput(args[DAYS]):
            channel = self.bot.get_channel(CHANNEL_ID)
            message = await getFirstEnzoMessage(channel)
            updatedContent = generateUpdatedContent(days := int(args[DAYS]))
            if message and message.author.id == ENZO_BOT_ID:
                await message.edit(content=updatedContent)
            else:
                await channel.purge()
                await channel.send(content=updatedContent, file=discord.File(IMAGE_PATH))
            self.unixTime += (getDayCounter(self.unixTime) - days) * SECONDS_IN_DAY
            saveToBinaryFile(BINARY_FILE_PATH, self.unixTime)


async def setup(bot: commands.Bot) -> None:
    """
    Initializes and adds Cog to Bot.
    """
    unixTime = loadBinaryFile(BINARY_FILE_PATH)
    await bot.add_cog(MessageUpdater(bot, unixTime))
