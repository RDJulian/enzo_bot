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
    try:
        return int(days) >= 0
    except ValueError:
        return False


def isValidTimeInput(*formattedTime: str) -> bool:
    try:
        valid = True
        i = 0
        while i < len(formattedTime) and valid:
            valid = (0 <= int(formattedTime[i]) <= MAX_TIME[i])
            i += 1
        return valid
    except ValueError:
        return False


def convertUnixToTime(unixTime: int) -> datetime.time:
    return datetime.fromtimestamp(unixTime, timezone.utc).time()


async def fetchFirstMessage(channel: discord.TextChannel) -> discord.Message | None:
    return await anext(channel.history(limit=SEARCH_LIMIT, oldest_first=True), None)


def generateDayCounter(unixTime: int) -> int:
    return int((time() - unixTime) / SECONDS_IN_DAY)


def generateUpdatedTimeInSeconds(*formattedTime: str) -> int:
    i = 0
    seconds = 0
    while i < len(formattedTime):
        seconds += int(formattedTime[i]) * TIME_IN_SECONDS[i]
        i += 1
    return seconds


def generateUpdatedContent(days: int) -> str:
    return f"{MESSAGE_FIRST_HALF}{days}{MESSAGE_SECOND_HALF}"


class MessageUpdater(commands.Cog):
    def __init__(self, bot: commands.Bot, unixTime: int) -> None:
        self.bot = bot
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime)).start()

    def updateLoopTime(self, unixTime: int) -> None:
        self.loop.cancel()
        self.unixTime = unixTime
        self.loop = self.loadLoop(convertUnixToTime(self.unixTime)).start()
        saveToBinaryFile(DAY_COUNTER_BINARY_PATH, self.unixTime)

    def loadLoop(self, loopTime: datetime.time) -> callable:

        @tasks.loop(time=loopTime)
        async def updateMessage() -> None:
            await self.refreshMessage()

        return updateMessage

    @commands.Cog.listener(name="on_ready")
    async def refreshMessage(self) -> None:
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
        if message.author.id != ENZO_BOT_ID and message.channel.id == RESERVED_CHANNEL_ID:
            await message.delete()

    @commands.Cog.listener(name="on_message_delete")
    async def restoreMessage(self, message: discord.Message) -> None:
        if message.author.id == ENZO_BOT_ID and message.channel.id == RESERVED_CHANNEL_ID:
            await self.bot.get_channel(message.channel.id).send(content=message.content,
                                                                file=discord.File(SIRIUS_IMAGE_PATH))

    @commands.command(name="refrescar")
    async def refreshMessageCommand(self, context: commands.Context) -> None:
        await self.refreshMessage()

    @commands.command(name="reiniciar")
    async def resetMessage(self, context: commands.Context) -> None:
        self.updateLoopTime(int(time()))
        await self.refreshMessage()

    @commands.command(name="modificar_dias")
    async def modifyDays(self, context: commands.Context, *args: str) -> None:
        if len(args) == VALID_DAY_INPUT and isValidDayInput(args[DAYS]):
            self.unixTime += (generateDayCounter(self.unixTime) - int(args[DAYS])) * SECONDS_IN_DAY
            saveToBinaryFile(DAY_COUNTER_BINARY_PATH, self.unixTime)
            await self.refreshMessage()

    @commands.command(name="modificar_hora")
    async def modifyTime(self, context: commands.Context, *args: str) -> None:
        if MIN_TIME_INPUT <= len(args) <= MAX_TIME_INPUT and isValidTimeInput(*args):
            updatedTime = generateUpdatedTimeInSeconds(*args)
            self.updateLoopTime(self.unixTime - (self.unixTime + TIMEZONE) % SECONDS_IN_DAY + updatedTime)
            await self.refreshMessage()


async def setup(bot: commands.Bot) -> None:
    data = loadBinaryFile(DAY_COUNTER_BINARY_PATH)
    if data:
        unixTime = data
    else:
        unixTime = int(time())
    await bot.add_cog(MessageUpdater(bot, unixTime))
