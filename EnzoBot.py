import asyncio
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from constants import *


async def loadCogs(bot: commands.Bot):
    """
    Loads all cogs to the bot.
    """
    for cog in COGS:
        await bot.load_extension(cog)


load_dotenv('token.env')
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
enzoBot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)

asyncio.run(loadCogs(enzoBot))
enzoBot.run(TOKEN)
