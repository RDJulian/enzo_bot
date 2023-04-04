import discord
from discord.ext import commands
from constants.constants import *


def isKeywordMentioned(content: str, keyword: str) -> bool:
    """
    :param keyword:
    :param content: Content from a discord.Message.
    Returns True if the content contains KEYWORD, ignoring uppercase characters. False otherwise.
    """
    words = content.lower().split()
    return True if keyword in words else False


class OnMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def onMessage(self, message: discord.Message) -> None:
        """
        Executes different actions based on channnel ID and message content.
        """
        if message.author.id != ENZO_BOT_ID:
            if message.channel.id == CHANNEL_ID:
                await message.delete()
            elif isKeywordMentioned(message.content, "enzo"):
                await message.channel.send(content=RESPONSE_TEXT)
            elif isKeywordMentioned(message.content, "huh"):
                await message.channel.send(file=discord.File("huh.png"))


async def setup(bot: commands.Bot) -> None:
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(OnMessageCog(bot))
