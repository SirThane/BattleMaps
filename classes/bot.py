
from discord.ext.commands import Bot as DiscordBot


class Bot(DiscordBot):

    def __init__(self, command_prefix, **kwargs):
        self.db = ""
        self.APP_NAME = ""
        self.app_info = None
        super().__init__(command_prefix, **kwargs)
