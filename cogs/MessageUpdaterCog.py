import datetime

import discord
from discord.ext import tasks, commands

from cogs.ResetCommandCog import getFirstEnzoMessage
from constants import *


def generateUpdatedContent(days: int) -> str:
    """
    Returns a newly generated text, with correct format and updated day counter.
    """
    return f"{MESSAGE_FIRST_HALF}{days}{MESSAGE_SECOND_HALF}"


class MessageUpdater(commands.Cog):
    def __init__(self, bot: commands.Bot, time, dayCounter):
        self.bot = bot
        self.loop = self.loadLoop(time).start()
        self.dayCounter = dayCounter

    def updateLoopTime(self, time):
        """
        Updates loop time by unloading old loop and reloading a new one with the desired time.
        """
        self.loop.cancel()
        self.loop = self.loadLoop(time).start()

    def loadLoop(self, time) -> callable:
        """
        Returns loop task with the desired time.
        """

        @tasks.loop(time=time)
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


async def setup(bot: commands.Bot):
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(MessageUpdater(bot, datetime.time(hour=3), 0))
