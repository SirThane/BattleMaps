"""Utility functions and classes.
"""

import sys
from contextlib import contextmanager
from io import StringIO, BytesIO
from re import match
from time import localtime, strftime

from aiohttp import ClientSession
import discord
from redis import StrictRedis as DefaultStrictRedis
from discord import TextChannel
from discord.ext.commands import BadArgument, Context, IDConverter
from discord.utils import get, find
from typing import Iterable, Tuple, Union


ZWSP = u'\u200b'


class Paginator:

    def __init__(
            self,
            page_limit: int = 1000,
            trunc_limit: int = 2000,
            headers=None,
            header_extender=u'\u200b'
    ):
        self.page_limit = page_limit
        self.trunc_limit = trunc_limit
        self._pages = None
        self._headers = None
        self._header_extender = header_extender
        self.set_headers(headers)

    @property
    def pages(self):
        if self._headers:
            self._extend_headers(len(self._pages))
            headers, self._headers = self._headers, None
            return [
                (headers[i], self._pages[i]) for i in range(len(self._pages))
            ]
        else:
            return self._pages

    def set_headers(self, headers=None):
        self._headers = headers

    def set_header_extender(self, header_extender: str = u'\u200b'):
        self._header_extender = header_extender

    def _extend_headers(self, length: int):
        while len(self._headers) < length:
            self._headers.append(self._header_extender)

    def set_trunc_limit(self, limit: int = 2000):
        self.trunc_limit = limit

    def set_page_limit(self, limit: int = 1000):
        self.page_limit = limit

    def paginate(self, value):
        """
        To paginate a string into a list of strings under
        `self.page_limit` characters. Total len of strings
        will not exceed `self.trunc_limit`.
        :param value: string to paginate
        :return list: list of strings under 'page_limit' chars
        """
        spl = str(value).split('\n')
        ret = []
        page = ''
        total = 0
        for i in spl:
            if total + len(page) < self.trunc_limit:
                if (len(page) + len(i)) < self.page_limit:
                    page += '\n{}'.format(i)
                else:
                    if page:
                        total += len(page)
                        ret.append(page)
                    if len(i) > (self.page_limit - 1):
                        tmp = i
                        while len(tmp) > (self.page_limit - 1):
                            if total + len(tmp) < self.trunc_limit:
                                total += len(tmp[:self.page_limit])
                                ret.append(tmp[:self.page_limit])
                                tmp = tmp[self.page_limit:]
                            else:
                                ret.append(tmp[:self.trunc_limit - total])
                                break
                        else:
                            page = tmp
                    else:
                        page = i
            else:
                ret.append(page[:self.trunc_limit - total])
                break
        else:
            ret.append(page)
        self._pages = ret
        return self.pages


def _get_from_guilds(bot, getter, argument):
    """Copied from discort.ext.commands.converter to prevent
    access to protected attributes inspection error"""
    result = None
    for guild in bot.guilds:
        result = getattr(guild, getter)(argument)
        if result:
            return result
    return result


class GlobalTextChannelConverter(IDConverter):
    """Converts to a :class:`~discord.TextChannel`.

    Copy of discord.ext.commands.converters.TextChannelConverter,
    Modified to always search global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    """
    async def convert(self, ctx: Context, argument: str) -> TextChannel:
        bot = ctx.bot

        search = self._get_id_match(argument) or match(r'<#([0-9]+)>$', argument)

        if match is None:
            # not a mention
            if ctx.guild:
                result = get(ctx.guild.text_channels, name=argument)
            else:
                def check(c):
                    return isinstance(c, TextChannel) and c.name == argument
                result = find(check, bot.get_all_channels())
        else:
            channel_id = int(search.group(1))
            if ctx.guild:
                result = ctx.guild.get_channel(channel_id)
            else:
                result = _get_from_guilds(bot, 'get_channel', channel_id)

        if not isinstance(result, discord.TextChannel):
            raise BadArgument('Channel "{}" not found.'.format(argument))

        return result


async def download_image(url: str, file_path: Union[bytes, str, BytesIO]) -> None:
    is_bytes = False
    if isinstance(file_path, str):
        fd = open(file_path, "wb")
    else:
        is_bytes = True
        fd = file_path

    try:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                while True:
                    chunk = await resp.content.read(10)
                    if not chunk:
                        break
                    fd.write(chunk)

        fd.seek(0)

    finally:
        if not is_bytes:
            fd.close()


def get_timestamp() -> str:
    return strftime("%a %b %d, %Y at %H:%M %Z", localtime())


@contextmanager
def stdoutio(file=None):
    old = sys.stdout
    if file is None:
        file = StringIO()
    sys.stdout = file
    yield file
    sys.stdout = old


def bool_str(arg):
    if arg == 'True':
        return True
    elif arg == 'False':
        return False
    else:
        return arg


def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x


def bytespop(
        b: Union[bytes, bytearray],
        q: int = 1,
        decode: str = None,
        endian: str = "little"
) -> Tuple[Union[int, str, bytearray], bytearray]:

    if isinstance(b, bytes):
        b = bytearray(b)

    ret = b[:q]

    b = b[q:]

    if decode == "utf8":
        return ret.decode("utf8"), b
    elif decode == "int":
        return int.from_bytes(ret, endian), b
    else:
        return ret, b


def bool_transform(arg):
    if isinstance(arg, str):
        return bool_str(arg)
    elif isinstance(arg, list):
        for i in range(len(arg)):
            arg[i] = bool_str(arg[i])
        return arg
    elif isinstance(arg, dict):
        for i in arg.keys():
            arg[i] = bool_str(arg[i])
        return arg


class StrictRedis(DefaultStrictRedis):
    """Turns 'True' and 'False' values returns
    in redis to bool values"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        # ret = eval(compile(ret, '<string>', 'eval'))
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret
