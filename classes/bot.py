
from discord.ext import commands


class Bot(commands.Bot):

    def __init__(self, command_prefix, **kwargs):
        self.db = ""
        self.APP_NAME = ""
        super().__init__(command_prefix, **kwargs)