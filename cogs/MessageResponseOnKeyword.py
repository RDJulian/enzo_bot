import discord
from discord.ext import commands
from constants.constants import ENZO_BOT_ID, RESERVED_CHANNEL_ID

RESPONSE_TEXT = "Yo"
HUH_IMAGE_PATH = "images/huh.png"
BANNED_CHANNELS = [RESERVED_CHANNEL_ID]


async def responseOnEnzo(message: discord.Message) -> None:
    """
    :param message: A discord Message.
    Executes response to Keyword.
    """
    await message.channel.send(content=RESPONSE_TEXT)


async def responseOnHuh(message: discord.Message) -> None:
    """
    :param message: A discord Message.
    Executes response to Keyword.
    """
    await message.channel.send(file=discord.File(HUH_IMAGE_PATH))


class OnMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        :param bot: A Discord commands.Bot.
        """
        self.bot = bot
        # Easily expandable by adding a lowercase keyword with a function implementation.
        self.responseTable = {"enzo": responseOnEnzo, "huh": responseOnHuh}

    def findKeywords(self, content: str) -> list[str]:
        """
        :param content: Content from a discord.Message.
        :return: List of found Keywords in content.
        Returns all found Keywords in the message.
        """
        words = content.lower().split()
        foundKeywords = [*set([word for word in words if word in self.responseTable.keys()])]
        return foundKeywords

    @commands.Cog.listener(name="on_message")
    async def responseOnKeyword(self, message: discord.Message) -> None:
        """
        :param message: A discord Message.
        Executes different actions based on channnel ID and message content.
        """
        if message.author.id != ENZO_BOT_ID and message.channel.id not in BANNED_CHANNELS:
            foundKeywords = self.findKeywords(message.content)
            for keyword in foundKeywords:
                await self.responseTable[keyword](message)


async def setup(bot: commands.Bot) -> None:
    """
    :param bot: A Discord commands.Bot.
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(OnMessageCog(bot))
