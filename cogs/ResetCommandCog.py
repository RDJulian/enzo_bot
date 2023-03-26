from discord.ext import commands
import discord

from constants import *


def generateUpdatedContent(days: int) -> str:
    """
    Returns a newly generated text, with correct format and updated day counter.
    """
    return f"{MESSAGE_FIRST_HALF}{days}{MESSAGE_SECOND_HALF}"


async def getFirstEnzoMessage(channel: discord.TextChannel) -> discord.Message | None:
    try:
        enzoMessage = [message async for message in channel.history(limit=1, oldest_first=True)][0]
        return enzoMessage if enzoMessage.author.id == ENZO_BOT_ID else None
    except IndexError:
        return None


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


class ResetCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await sendInitialMessage(channel)

    @commands.command(name="sumar")
    async def resetMessage(self, ctx) -> None:
        """
        :param ctx: discord.Message context, unused.
        Resets the message to INITIAL_MESSAGE by modifying it. If it doesn't exist or the last one isn't from Enzo's ID,
        sends a new one.
        """
        channel = self.bot.get_channel(CHANNEL_ID)
        message = await getFirstEnzoMessage(channel)
        updatedContent = generateUpdatedContent(69)
        if message and message.author.id == ENZO_BOT_ID:
            await message.edit(content=updatedContent)
        else:
            await channel.send(content=updatedContent, file=discord.File(IMAGE_PATH))


async def setup(bot: commands.Bot):
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(ResetCommandCog(bot))
