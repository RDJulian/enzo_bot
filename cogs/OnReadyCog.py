import discord
from discord.ext import commands


class OnReadyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def onReady(self) -> None:
        """
        Changes game activity to desired name.
        """
        await self.bot.change_presence(activity=discord.Game(name="el Pepe"))


async def setup(bot: commands.Bot):
    """
    Initializes and adds Cog to Bot.
    """
    await bot.add_cog(OnReadyCog(bot))
