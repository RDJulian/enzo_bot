import discord
from discord.ext import commands
from constants import *


def isEnzoMentioned(content: str) -> bool:
    """
    :param content: Content from a discord.Message.
    :return: True if the content contains keyword "enzo", ignoring uppercase characters. False otherwise.
    """
    return True if content.lower().find("enzo") != -1 else False


class OnMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def onMessage(self, message: discord.Message):
        """
        Executes different actions based on channnel ID and message content.
        """
        if message.author.id != ENZO_BOT_ID:
            if message.channel.id == CHANNEL_ID:
                await message.delete()
            elif isEnzoMentioned(message.content):
                await message.channel.send(content="Yo")


async def setup(bot: commands.Bot):
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(OnMessageCog(bot))
