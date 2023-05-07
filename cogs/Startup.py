import discord
from discord.ext import commands

ACTIVITY_NAME = "el Pepe"


class Startup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        :param bot: A Discord commands.Bot.
        """
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def startup(self) -> None:
        """
        Changes game activity to the desired ACTIVITY_NAME.
        """
        await self.bot.change_presence(activity=discord.Game(name=ACTIVITY_NAME))


async def setup(bot: commands.Bot) -> None:
    """
    :param bot: A Discord commands.Bot.
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(Startup(bot))
