
from __future__ import annotations

from traceback import extract_tb

from discord.channel import TextChannel
from discord.colour import Colour
from discord.embeds import Embed
from discord.errors import DiscordException, LoginFailure
from discord.ext.commands import Bot as DiscordBot
from discord.ext.commands.context import Context
from discord.message import Message
from typing import Union

from utils.utils import ZWSP


class ErrorLog:

    def __init__(self, bot, channel: Union[int, str, TextChannel]):
        self.bot = bot
        if isinstance(channel, int):
            channel = self.bot.get_channel(channel)
        elif isinstance(channel, str):
            channel = self.bot.get_channel(int(channel))
        if isinstance(channel, TextChannel):
            self.channel = channel
        else:
            self.channel = None

    async def send(self, error: Union[Exception, DiscordException], ctx: Context = None) -> Message:
        if not self.channel:
            raise AttributeError("ErrorLog channel not set")
        em = await self.em_tb(error, ctx)
        return await self.channel.send(embed=em)

    @staticmethod
    async def em_tb(error: Union[Exception, DiscordException], ctx: Context = None) -> Embed:
        if ctx:
            prefix = await ctx.bot.get_prefix(ctx.message)
            title = f"In {prefix}{ctx.command.qualified_name}"
            description = f"**{error.__class__.__name__}**: {error}"
        else:
            title = None
            description = f"**{type(error).__name__}**: {str(error)}"

        stack = extract_tb(error.__traceback__)
        tb_fields = [
            {
                "name": f"{ZWSP}\n__{fn}__",
                "value": f"Line `{ln}` in `{func}`:\n```py\n{txt}\n```",
                "inline": False
            } for fn, ln, func, txt in stack
        ]

        em = Embed(color=Colour.red(), title=title, description=f"{description}")

        for field in tb_fields:
            em.add_field(**field)

        return em


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

        # Get the channel ready for errorlog
        # Bot.get_channel method not available until on_ready
        self.errorlog_channel = kwargs.pop("errorlog", None)
        self.errorlog = None

        # Changed signature from arg to kwarg so I can splat the hgetall from db in main.py
        command_prefix = kwargs.pop("command_prefix", "!")

        super().__init__(command_prefix, **kwargs)

    def run(self, **kwargs):
        # Changed signature from arg to kwarg so I can splat the hgetall from db in main.py
        token = kwargs.pop("token", None)
        if not token:
            raise LoginFailure("No or improper token passed")
        super().run(token, **kwargs)
