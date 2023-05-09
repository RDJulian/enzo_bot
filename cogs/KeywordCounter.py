import discord
from discord.ext import commands
from binaryFileHandler import saveToBinaryFile, loadBinaryFile
from constants.constants import ENZO_BOT_ID, RESERVED_CHANNEL_ID
from constants.keywordCounterConstants import *

KEYWORD_COUNTER_BINARY_PATH = "binary/keywordCounter.dat"
BANNED_CHANNELS = [RESERVED_CHANNEL_ID]
DATA_FIELDS = 2
KEYWORDS = 0
SORTED = 1


def searchNewKeywords(content: str) -> str:
    """
    :param content: Content from a discord.Message.
    :return: Potential new Keywords to add.
    Searches and yields potentially new Keywords from the content.
    """
    words = content.lower().split()
    for word in words:
        i = 0
        added = False
        while i < len(NEW_KEYWORD_TRIGGERS) and not added:
            if word.find(NEW_KEYWORD_TRIGGERS[i]) != -1:
                yield word
                added = True
            i += 1


class KeywordCounter(commands.Cog):
    def __init__(self, bot: commands.Bot, keywords: dict, isSorted: bool) -> None:
        """
        :param bot: A Discord commands.Bot.
        :param keywords: Dictionary of Keywords with counters as values.
        :param isSorted: bool indicating if Keywords is sorted.
        """
        self.bot = bot
        self.keywords = keywords
        self.sorted = isSorted

    @commands.Cog.listener(name="on_message")
    async def updateKeywordsCounters(self, message: discord.Message) -> None:
        """
        :param message: A discord Message.
        Adds potentially new Keywords and updates all counters for detected Keywords in the message content.
        """
        if message.author.id != ENZO_BOT_ID and message.content != f"!{SHOW_KEYWORDS_COMMAND}":
            self.addNewKeywords(message.content)
            if self.updateKeywords(message.content):
                self.sorted = False
                saveToBinaryFile(KEYWORD_COUNTER_BINARY_PATH, (self.keywords, self.sorted))

    def addNewKeywords(self, content: str) -> None:
        """
        :param content: Content from a discord.Message.
        Adds potentially new Keywords to the dictionary.
        """
        for newKeyword in searchNewKeywords(content):
            if newKeyword not in self.keywords.keys():
                self.keywords[newKeyword] = 0

    def updateKeywords(self, content: str) -> bool:
        """
        :param content: Content from a discord.Message.
        :return: bool.
        Updates all counters for detected Keywords in the message content. If there is any change, returns True.
        """
        words = content.lower().split()
        updated = False
        for word in words:
            if word in self.keywords.keys():
                self.keywords[word] += 1
                updated = True
        return updated

    @commands.command(name=SHOW_KEYWORDS_COMMAND)
    async def showKeywords(self, context: commands.Context) -> None:
        """
        :param context: Context from the command call.
        Shows all Keywords and counters in descending order.
        """
        if context.channel.id not in BANNED_CHANNELS:
            self.sortKeywords()
            output = self.generateOutputText()
            if output:
                await context.channel.send(content=output)

    def sortKeywords(self) -> None:
        """
        Sorts the Keywords dictionary in descending order.
        """
        if not self.sorted:
            self.keywords = {keyword: counter for keyword, counter in
                             sorted(self.keywords.items(), reverse=True, key=lambda item: item[1])}
            self.sorted = True

    def generateOutputText(self) -> str:
        """
        :return: A formatted string.
        Generates a formatted string containing a keyword, and it's counter.
        """
        output = ""
        for keyword, counter in self.keywords.items():
            if not counter == 0:
                output += f"{keyword} fue mencionado {counter} vece(s).\n"
        return output


async def setup(bot: commands.Bot) -> None:
    """
    :param bot: A Discord commands.Bot.
    Initializes and adds Cog to Bot.
    """
    data = loadBinaryFile(KEYWORD_COUNTER_BINARY_PATH)
    if data and len(data) == DATA_FIELDS:
        keywords = data[KEYWORDS]
        isSorted = data[SORTED]
    else:
        keywords = INITIAL_KEYWORD_COUNTER
        isSorted = False
    await bot.add_cog(KeywordCounter(bot, keywords, isSorted))
