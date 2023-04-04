import discord
from discord.ext import commands
from binaryFileHandler import saveToBinaryFile, loadBinaryFile
from constants.constants import *
from constants.keywordConstants import *


def isKeywordMentioned(content: str, keyword: str) -> bool:
    """
    :param keyword:
    :param content: Content from a discord.Message.
    Returns True if the content contains KEYWORD, ignoring uppercase characters. False otherwise.
    """
    words = content.lower().split()
    return True if keyword in words else False


def searchNewKeywords(content: str) -> list[str]:
    words = content.lower().split()
    newKeywords = []
    for word in words:
        for trigger in NEW_KEYWORD_TRIGGERS:
            if word.find(trigger) != -1:
                newKeywords.append(word)
    return newKeywords


class KeywordCounterCog(commands.Cog):
    def __init__(self, bot: commands.Bot, keywords: dict) -> None:
        self.bot = bot
        self.keywords = keywords

    @commands.Cog.listener(name="on_message")
    async def keywordInMessage(self, message: discord.Message) -> None:
        """
        Executes different actions based on channnel ID and message content.
        """
        if message.author.id != ENZO_BOT_ID and message.content != f"!{SHOW_KEYWORDS_COMMAND}":
            newKeywords = searchNewKeywords(message.content)
            if len(newKeywords) != 0:
                for newKeyword in newKeywords:
                    if newKeyword not in self.keywords.keys():
                        self.keywords[newKeyword] = 0
            for keyword in self.keywords:
                if isKeywordMentioned(message.content, keyword):
                    self.keywords[keyword] += 1
                    saveToBinaryFile(KEYWORD_COUNTER_BINARY_PATH, self.keywords)

    @commands.command(name=SHOW_KEYWORDS_COMMAND)
    async def showKeywords(self, context: commands.Context) -> None:
        if not context.channel.id == CHANNEL_ID:
            self.keywords = {keyword: counter for keyword, counter in
                             sorted(self.keywords.items(), reverse=True, key=lambda item: item[1])}
            output = ""
            for keyword, counter in self.keywords.items():
                if not counter == 0:
                    output += f"{keyword} fue mencionado {counter} vece(s).\n"
            if output != "":
                await context.channel.send(content=output)


async def setup(bot: commands.Bot) -> None:
    """
    Initializes and adds Cog to Bot.
    """
    keywords = loadBinaryFile(KEYWORD_COUNTER_BINARY_PATH)
    if not keywords:
        keywords = INITIAL_KEYWORD_COUNTER
    await bot.add_cog(KeywordCounterCog(bot, keywords))
