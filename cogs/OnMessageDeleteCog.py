import discord
from discord.ext import commands
from constants import *


class OnMessageDeleteCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_message_delete")
    async def onMessageDelete(self, message: discord.Message) -> None:
        """
        Restores Enzo's message if its deleted.
        """
        if message.author.id == ENZO_BOT_ID and message.channel.id == CHANNEL_ID:
            await self.bot.get_channel(CHANNEL_ID).send(content=message.content,
                                                        file=discord.File(IMAGE_PATH))


async def setup(bot: commands.Bot):
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(OnMessageDeleteCog(bot))
