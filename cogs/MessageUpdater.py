import discord
from datetime import datetime, time, timezone
from time import time
from discord.ext import commands, tasks
from binaryFileHandler import loadBinaryFile, saveToBinaryFile
from constants.constants import ORURA_ID, RESERVED_CHANNEL_ID, ENZO_BOT_ID

# Message
INITIAL_MESSAGE = f'El "Dia del Accidente" es cuando a <@{ORURA_ID}> le da o se pelea con alguien y ' \
                  'semi-borra usuarios del server porque esta enojada/triste/retrasada mental.\n\nActualmente ' \
                  'pasaron **0** día(s) desde el último accidente.'

MESSAGE_FIRST_HALF = f'El "Dia del Accidente" es cuando a <@{ORURA_ID}> le da o se pelea con alguien y ' \
                     'semi-borra usuarios del server porque esta enojada/triste/retrasada mental.\n\nActualmente ' \
                     'pasaron **'

MESSAGE_SECOND_HALF = f"** día(s) desde el último accidente."

# Paths
SIRIUS_IMAGE_PATH = "images/sirius_black.png"
DAY_COUNTER_BINARY_PATH = "binary/dayCounter.dat"

# Time
TIMEZONE = -10800
SECONDS_IN_DAY = 86400
MAX_TIME = [23, 59, 59]
TIME_IN_SECONDS = [3600, 60, 1]

# Index
DAYS = 0

# Limits
SEARCH_LIMIT = 1
MIN_TIME_INPUT = 1
MAX_TIME_INPUT = 3
VALID_DAY_INPUT = 1


def isValidDayInput(days: str) -> bool:
    """
    :param days: String that may be an integer.
    :return: bool.
    Returns True if the input text is valid i.e. can be cast to int and greater or equal to zero. False otherwise.
    """
    try:
        return int(days) >= 0
    except ValueError:
        return False


def isValidTimeInput(*formattedTime: str) -> bool:
    """
    :param formattedTime: 1 to 3 string arguments that may be integers.
    :return: bool.
    Returns True if the input text is valid i.e. all arguments can be cast to int and each has correct values (hours
    between 0 and 23, etc.). False otherwise.
    """
    try:
        valid = True
        i = 0
        while i < len(formattedTime) and valid:
            valid = (0 <= int(formattedTime[i]) <= MAX_TIME[i])
            i += 1
        return valid
    except ValueError:
        return False


def convertUnixToTime(unixTime: int) -> time:
    """
    :param unixTime: Specific time in Unix (seconds since epoch).
    :return: A time object.
    Converts unixTime to time object i.e. without date and returns it. Offsets to UTC.
    """
    return datetime.fromtimestamp(unixTime, timezone.utc).time()


async def fetchFirstMessage(channel: discord.TextChannel) -> discord.Message | None:
    """
    :param channel: A Discord Text Channel.
    :return: A Discord Message.
    Returns the first message from the desired channel. If the message can't be fetched, returns None.
    """
    return await anext(channel.history(limit=SEARCH_LIMIT, oldest_first=True), None)


def generateDayCounter(unixTime: int) -> int:
    """
    :param unixTime: Specific time in Unix (seconds since epoch).
    :return: A day counter.
    Calculates difference between current and saved time, rounded in days, and returns it.
    """
    return int((time() - unixTime) / SECONDS_IN_DAY)


def generateUpdatedTimeInSeconds(*formattedTime: str) -> int:
    """
    :param formattedTime: 1 to 3 string arguments that can be cast to integers.
    :return: A seconds value.
    Converts arguments (formatted in hours, minutes, seconds) to seconds and returns it.
    """
    i = 0
    seconds = 0
    while i < len(formattedTime):
        seconds += int(formattedTime[i]) * TIME_IN_SECONDS[i]
        i += 1
    return seconds


def generateUpdatedContent(days: int) -> str:
    """
    :param days: A day counter.
    :return: A formatted string.
    Returns a newly generated text, with correct format and updated day counter.
    """
    return f"{MESSAGE_FIRST_HALF}{days}{MESSAGE_SECOND_HALF}"


class MessageUpdater(commands.Cog):
    def __init__(self, bot: commands.Bot, unixTime: int) -> None:
        """
        :param bot: A Discord commands.Bot.
        :param unixTime: Specific time in Unix (seconds since epoch). Represents the timestamp of the accident.
        """
        self.bot = bot
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime)).start()

    def updateLoopTime(self, unixTime: int) -> None:
        """
        :param unixTime: Specific time in Unix (seconds since epoch).
        Updates loop time by unloading old loop and reloading a new one with the desired Unix time, then saves it.
        """
        self.loop.cancel()
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime)).start()
        saveToBinaryFile(DAY_COUNTER_BINARY_PATH, self.unixTime)

    def loadLoop(self, loopTime: datetime.time) -> callable:
        """
        :param loopTime: Time representing task loop trigger.
        :return: Callable method.
        Returns loop task with the desired time trigger.
        """

        @tasks.loop(time=loopTime)
        async def updateMessage() -> None:
            """
            Updates the day counting message, adding one to the counter. Logic is the same as self.refreshMessage(), so
            it just recalls.
            """
            await self.refreshMessage()

        return updateMessage

    @commands.Cog.listener(name="on_ready")
    async def refreshMessage(self) -> None:
        """
        Refreshes the message by modifying it. It's content may not change. If it doesn't exist or the last one isn't
        from Enzo's ID, wipes channel and sends a new one.
        """
        channel = self.bot.get_channel(RESERVED_CHANNEL_ID)
        message = await fetchFirstMessage(channel)
        updatedContent = generateUpdatedContent(generateDayCounter(self.unixTime))
        if message and message.author.id == ENZO_BOT_ID:
            await message.edit(content=updatedContent)
        else:
            await channel.purge()
            await channel.send(content=updatedContent, file=discord.File(SIRIUS_IMAGE_PATH))

    @commands.Cog.listener(name="on_message")
    async def deleteMessageOnChannel(self, message: discord.Message) -> None:
        """
        :param message: A Discord Message.
        Deletes message if it was sent in RESERVED_CHANNEL_ID and isn't from the Bot.
        """
        if message.author.id != ENZO_BOT_ID and message.channel.id == RESERVED_CHANNEL_ID:
            await message.delete()

    @commands.Cog.listener(name="on_message_delete")
    async def restoreMessage(self, message: discord.Message) -> None:
        """
        :param message: A Discord Message.
        Restores message if it was sent in RESERVED_CHANNEL_ID and is from the Bot.
        """
        if message.author.id == ENZO_BOT_ID and message.channel.id == RESERVED_CHANNEL_ID:
            await self.bot.get_channel(message.channel.id).send(content=message.content,
                                                                file=discord.File(SIRIUS_IMAGE_PATH))

    @commands.command(name="refrescar")
    async def refreshMessageCommand(self, _context: commands.Context) -> None:
        """
        :param _context: unused.
        Command for manually refreshing the message.
        """
        await self.refreshMessage()

    @commands.command(name="reiniciar")
    async def resetMessage(self, _context: commands.Context) -> None:
        """
        :param _context: unused.
        Resets accident time to current time, then refreshes the message.
        """
        self.updateLoopTime(int(time()))
        await self.refreshMessage()

    @commands.command(name="modificar_dias")
    async def modifyDays(self, _context: commands.Context, *args: str) -> None:
        """
        :param _context: unused.
        :param args: String arguments that may represent an integer.
        If input is valid, modifies accident time to match the desired day count, then refreshes the message.
        """
        if len(args) == VALID_DAY_INPUT and isValidDayInput(args[DAYS]):
            self.unixTime += (generateDayCounter(self.unixTime) - int(args[DAYS])) * SECONDS_IN_DAY
            saveToBinaryFile(DAY_COUNTER_BINARY_PATH, self.unixTime)
            await self.refreshMessage()

    @commands.command(name="modificar_hora")
    async def modifyTime(self, _context: commands.Context, *args: str) -> None:
        """
        :param _context: unused.
        :param args: String arguments that may represent a formatted time (hours, minutes, seconds).
        If input is valid, modifies accident loop time to match desired time, then refreshes the message.
        """
        if MIN_TIME_INPUT <= len(args) <= MAX_TIME_INPUT and isValidTimeInput(*args):
            updatedTime = generateUpdatedTimeInSeconds(*args)
            self.updateLoopTime(self.unixTime - (self.unixTime + TIMEZONE) % SECONDS_IN_DAY + updatedTime)
            await self.refreshMessage()


async def setup(bot: commands.Bot) -> None:
    """
    :param bot: A Discord commands.Bot.
    Initializes and adds Cog to Bot.
    """
    data = loadBinaryFile(DAY_COUNTER_BINARY_PATH)
    if data:
        unixTime = data
    else:
        unixTime = int(time())
    await bot.add_cog(MessageUpdater(bot, unixTime))
