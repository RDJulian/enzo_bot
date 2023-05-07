import discord
from datetime import datetime, time, timezone
from time import time
from discord.ext import commands, tasks
from binaryFileHandler import loadBinaryFile, saveToBinaryFile
from constants.constants import *


def isValidDayInput(days: str) -> bool:
    """
    Returns True if the input text is valid i.e. can be cast to int and greater or equal to zero. False otherwise.
    """
    try:
        return int(days) >= 0
    except ValueError:
        return False


async def fetchFirstEnzoMessage(channel: discord.TextChannel) -> discord.Message | None:
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
    Converts unixTime to time object i.e. without date and returns it. Offsets to UTC.
    """
    return datetime.fromtimestamp(unixTime, timezone.utc).time()


def getDayCounter(unixTime: int) -> int:
    """
    Calculates difference between current and saved time, rounded in days, and returns it.
    """
    return int((time() - unixTime) / SECONDS_IN_DAY)


def isValidHourInput(*hour: str) -> bool:
    try:
        valid = True
        i = 0
        while i < len(hour) and valid:
            valid = (0 <= int(hour[i]) <= MAX_TIME[i])
            i += 1
        return valid
    except ValueError:
        return False


def generateUpdatedHour(*hour: str) -> int:
    i = 0
    seconds = 0
    while i < len(hour):
        seconds += int(hour[i]) * TIME_IN_SECONDS[i]
        i += 1
    return seconds


# TODO: Complete documentation.
class MessageUpdater(commands.Cog):
    def __init__(self, bot: commands.Bot, unixTime: int) -> None:
        self.bot = bot
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime)).start()

    def updateLoopTime(self, unixTime: int) -> None:
        """
        Updates loop time by unloading old loop and reloading a new one with the desired Unix time, then saves it.
        """
        self.loop.cancel()
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime)).start()
        saveToBinaryFile(DAY_COUNTER_BINARY_PATH, self.unixTime)

    def loadLoop(self, loopTime: datetime.time) -> callable:
        """
        Returns loop task with the desired time.
        """

        @tasks.loop(time=loopTime)
        async def updateMessage() -> None:
            """
            Updates the day counting message, adding one to the counter. If it doesn't exist or last message isn't from
            Enzo, wipes channel and generates a new one. Logic is the same as self.refreshMessage(), so it just recalls.
            """
            await self.refreshMessage()

        return updateMessage

    @commands.Cog.listener(name="on_ready")
    async def refreshMessage(self) -> None:
        """
        Refreshes the message by modifying it. It's content may not change. If it doesn't exist or the last one isn't
        from Enzo's ID, wipes channel and sends a new one.
        """
        channel = self.bot.get_channel(CHANNEL_ID)
        message = await fetchFirstEnzoMessage(channel)
        updatedContent = generateUpdatedContent(getDayCounter(self.unixTime))
        if message and message.author.id == ENZO_BOT_ID:
            await message.edit(content=updatedContent)
        else:
            await channel.purge()
            await channel.send(content=updatedContent, file=discord.File(SIRIUS_IMAGE_PATH))

    @commands.command(name="reiniciar")
    async def resetMessage(self, context: commands.Context) -> None:
        """
        :param context: unused.
        Resets the message to INITIAL_MESSAGE by modifying it. If it doesn't exist or the last one isn't from Enzo's ID,
        wipes channel and sends a new one.
        """
        self.updateLoopTime(int(time()))
        await self.refreshMessage()

    @commands.command(name="refrescar")
    async def refreshMessageCommand(self, context: commands.Context) -> None:
        """
        :param context: unused.
        Simply recalls self.refreshMessage(). This avoids repeated code.
        """
        await self.refreshMessage()

    @commands.command(name="modificar_dias")
    async def modifyDays(self, context: commands.Context, *args: str) -> None:
        """
        :param args: days: str. Castable to int and greater or equal to zero only.
        :param context: unused.
        Modifies the message with the desired day counter by modifying it. If it doesn't exist or the last one isn't
        from Enzo's ID, wipes channel and sends a new one. Meant as a debug command.
        """
        if len(args) == 1 and isValidDayInput(args[DAYS]):
            self.unixTime += (getDayCounter(self.unixTime) - int(args[DAYS])) * SECONDS_IN_DAY
            saveToBinaryFile(DAY_COUNTER_BINARY_PATH, self.unixTime)
            await self.refreshMessage()

    @commands.command(name="modificar_hora")
    async def modifyHour(self, context: commands.Context, *args: str) -> None:
        if 1 <= len(args) <= 3 and isValidHourInput(*args):
            updatedHour = generateUpdatedHour(*args)
            self.updateLoopTime(self.unixTime - (self.unixTime + TIMEZONE) % SECONDS_IN_DAY + updatedHour)
            await self.refreshMessage()

    @commands.Cog.listener(name="on_message_delete")
    async def restoreMessage(self, message: discord.Message) -> None:
        """
        Restores Enzo's message if it was deleted.
        TODO: Search if it's possible to reuse the attached image. It would make this command more generic.
            Also consider if injecting dependency would be better.
        """
        if message.author.id == ENZO_BOT_ID and message.channel.id == CHANNEL_ID:
            await self.bot.get_channel(message.channel.id).send(content=message.content,
                                                                file=discord.File(SIRIUS_IMAGE_PATH))


async def setup(bot: commands.Bot) -> None:
    """
    Initializes and adds Cog to Bot.
    """
    unixTime = loadBinaryFile(DAY_COUNTER_BINARY_PATH)
    load_dotenv('token.env')
    if not unixTime:
        unixTime = int(time())
    await bot.add_cog(MessageUpdater(bot, unixTime))
