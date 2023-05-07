import discord
from os import listdir
from asyncio import run
from discord.ext import commands
from constants.constants import TOKEN

COMMAND_PREFIX = "!"
COGS_DIR = "cogs/"


# This should be wrapped in a function/class but works for now.

async def loadCogs(bot: commands.Bot) -> None:
    """
    :param bot: A Discord commands.Bot.
    :return: None.
    Loads all Cogs in COGS_DIR to the bot.
    """
    cogs = listdir(COGS_DIR)
    for file in cogs:
        if file.endswith(".py"):
            cogName = file[:-3]
            await bot.load_extension(f"cogs.{cogName}")


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

enzoBot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)
run(loadCogs(enzoBot))
enzoBot.run(TOKEN)
