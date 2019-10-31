
from discord.errors import LoginFailure
from discord.ext.commands import Bot as DiscordBot


class Bot(DiscordBot):

    def __init__(self, **kwargs):
        self.db = kwargs.pop("db", None)
        self.APP_NAME = kwargs.pop("app_name")
        self.dm_help = kwargs.pop('dm_help', False) or kwargs.pop('pm_help', False)
        self.pm_help = self.dm_help

        # Declaring first. This will not be able to get set until login
        self.app_info = None

        # Changed signature from arg to kwarg so I can splat the hgetall from db in main.py
        command_prefix = kwargs.pop("command_prefix", "!")

        super().__init__(command_prefix, **kwargs)

    def run(self, **kwargs):
        # Changed signature from arg to kwarg so I can splat the hgetall from db in main.py
        token = kwargs.pop("token", None)
        if not token:
            raise LoginFailure("No or improper token passed")
        super().run(token, **kwargs)
