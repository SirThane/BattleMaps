
from __future__ import annotations

from traceback import extract_tb

from asyncio import sleep
from discord.channel import TextChannel
from discord.colour import Colour
from discord.embeds import Embed as DiscordEmbed
from discord.errors import DiscordException, LoginFailure
from discord.ext.commands import Bot as DiscordBot
from discord.ext.commands.context import Context
from discord.message import Message
from typing import List, Union

from utils.utils import ZWSP


class Embed(DiscordEmbed):

    def copy(self):
        """Returns a shallow copy of the embed.

        Must copy the method from discord.Embed, or it would
        return a copy of the super class."""
        return Embed.from_dict(self.to_dict())

    def strip_head(self):
        self.title = ""
        self.description = ""
        self.set_author(name="", url="", icon_url="")
        self.set_thumbnail(url="")

    def strip_foot(self):
        self.set_image(url="")
        self.set_footer(text="", icon_url="")

    def split(self) -> List[Embed]:
        title = len(self.title) if self.title else 0
        desc = len(self.description) if self.description else 0
        author_name = len(self.author.name) if self.author.name else 0
        author_url = len(self.author.url) if self.author.url else 0
        author_icon_url = len(self.author.icon_url) if self.author.icon_url else 0
        thumbnail = len(self.thumbnail.url) if self.thumbnail.url else 0

        image = len(self.image.url) if self.image.url else 0
        footer_text = len(self.footer.text) if self.footer.text else 0
        footer_icon_url = len(self.footer.icon_url) if self.footer.icon_url else 0

        field_lengths = [len(field.name) + len(field.value) for field in self.fields]

        head = sum((title, desc, author_name, author_url, author_icon_url, thumbnail))
        foot = sum((image, footer_text, footer_icon_url))

        if head + foot + sum(field_lengths) < 6000:
            return [self]

        char_count = head

        pages = list()
        page = self.copy()

        fields = [field.copy() for field in self.to_dict().get("fields", None)]

        page.clear_fields()
        page.strip_foot()

        for i, field in enumerate(fields):

            if char_count + field_lengths[i] < 6000:
                page.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )
                char_count += field_lengths[i]

            else:
                pages.append(page)

                page = self.copy()
                page.strip_head()
                page.clear_fields()
                page.strip_foot()

                page.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )
                char_count = field_lengths[i]

        if char_count + foot < 6000:
            page.set_footer(
                text=self.footer.text,
                icon_url=self.footer.icon_url
            )
            pages.append(page)

        else:
            pages.append(page)

            page = self.copy()
            page.strip_head()
            page.clear_fields()

            pages.append(page)

        return pages


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
        for i, page in enumerate(em.split()):
            if i:
                await sleep(0.1)
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
