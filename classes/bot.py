
from discord.errors import LoginFailure
from discord.ext.commands import Bot as DiscordBot


class Bot(DiscordBot):

    def __init__(self, **kwargs):

        # Redis db instance made available to cogs
        self.db = kwargs.pop("db", None)

        # Name of bot stored in Bot instance
        # Used as key name for db
        self.APP_NAME = kwargs.pop("app_name", None)

        # Legacy compatibility for Help command
        self.dm_help = kwargs.pop('dm_help', False) or kwargs.pop('pm_help', False)
        self.pm_help = self.dm_help

        # Used by timer cog
        self.secs = 0

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
