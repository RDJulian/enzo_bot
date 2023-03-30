import discord
from discord.ext import commands
from constants import *


class OnStartupCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def onStartup(self) -> None:
        """
        Changes game activity to the desired ACTIVITY_NAME.
        """
        await self.bot.change_presence(activity=discord.Game(name=ACTIVITY_NAME))


async def setup(bot: commands.Bot) -> None:
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(OnStartupCog(bot))
