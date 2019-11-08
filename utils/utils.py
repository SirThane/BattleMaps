"""Utility functions and classes.
"""

import sys
from contextlib import contextmanager
from io import StringIO, BytesIO
from re import match
from time import localtime, strftime

from aiohttp import ClientSession
from redis import StrictRedis as DefaultStrictRedis
from discord import TextChannel
from discord.ext.commands import BadArgument, Context, IDConverter
from discord.utils import get, find
from typing import Any, Generator, Iterable, Tuple, Union, Set, List, Dict

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

        if not isinstance(result, TextChannel):
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

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        # ret = eval(compile(ret, '<string>', 'eval'))
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret


class SubRedis:

    def __init__(self, db: StrictRedis, basekey: str):
        self.db = db
        self.basekey = basekey

    """ ###############
         Managing Keys
        ############### """

    def exists(self, *names: str) -> int:
        """Returns the number of ``names`` that exist"""
        names = [f"{self.basekey}:{name}" for name in names]
        return self.db.exists(*names)

    def delete(self, *names: str) -> Any:
        """Delete one or more keys specified by ``names``"""
        names = [f"{self.basekey}:{name}" for name in names]
        return self.db.delete(*names)

    """ ###########
         Iterators
        ########### """

    def scan_iter(self, pattern: str = None, count: int = None) -> Generator[str, str, None]:
        """
        Make an iterator using the SCAN command so that the client doesn't
        need to remember the cursor position.

        ``pattern`` allows for filtering the keys by pattern

        ``count`` allows for hint the minimum number of returns
        """
        if not pattern == "*":
            pattern = f":{pattern}"
        for item in self.db.scan_iter(f"{self.basekey}{pattern}", count):
            yield item.replace(f"{self.basekey}:", "")

    """ ###############
         Simple Values
        ############### """

    def set(self, name: str, value: str, ex: int = None, px: int = None, nx: bool = False, xx: bool = False) -> Any:
        """
        Set the value at key ``name`` to ``value``

        ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds.

        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.

        ``nx`` if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist.

        ``xx`` if set to True, set the value at key ``name`` to ``value`` only
            if it already exists.
        """
        return self.db.set(f"{self.basekey}:{name}", value, ex, px, nx, xx)

    def get(self, name: str) -> str:
        """Return the value at key ``name``, or None if the key doesn't exist"""
        return self.db.get(f"{self.basekey}:{name}")

    """ ######
         Sets
        ###### """

    def scard(self, name: str) -> int:
        """Return the number of elements in set ``name``"""
        return self.db.scard(f"{self.basekey}:{name}")

    def sismember(self, name: str, value: str) -> bool:
        """Return a boolean indicating if ``value`` is a member of set ``name``"""
        return self.db.sismember(f"{self.basekey}:{name}", value)

    def smembers(self, names: str) -> Set[str]:
        """Return all members of the set ``name``"""
        return self.db.smembers(f"{self.basekey}:{names}")

    def sadd(self, name: str, *values: str) -> Any:
        """Add ``value(s)`` to set ``name``"""
        return self.db.sadd(f"{self.basekey}:{name}", *values)

    def srem(self, name: str, *values: str) -> Any:
        """Remove ``values`` from set ``name``"""
        return self.db.srem(f"{self.basekey}:{name}", *values)

    """ #######
         Lists
        ####### """

    def lrange(self, name: str, start: int, end: int) -> List[str]:
        """
        Return a slice of the list ``name`` between
        position ``start`` and ``end``

        ``start`` and ``end`` can be negative numbers just like
        Python slicing notation
        """
        return self.db.lrange(f"{self.basekey}:{name}", start, end)

    def lpush(self, name: str, *values: str) -> Any:
        """Push ``values`` onto the head of the list ``name``"""
        return self.db.lpush(f"{self.basekey}:{name}", *values)

    def lrem(self, name: str, count: int, value: str) -> Any:
        """
        Remove the first ``count`` occurrences of elements equal to ``value``
        from the list stored at ``name``.

        The count argument influences the operation in the following ways:
            count > 0: Remove elements equal to value moving from head to tail.
            count < 0: Remove elements equal to value moving from tail to head.
            count = 0: Remove all elements equal to value.
        """
        return self.db.lrem(f"{self.basekey}:{name}", count, value)

    """ #############################
         Hashes (Dict-like Mappings)
        ############################# """

    def hget(self, name: str, key: str) -> str:
        """Return the value of ``key`` within the hash ``name``"""
        return self.db.hget(f"{self.basekey}:{name}", key)

    def hkeys(self, name: str) -> List[str]:
        """Return the list of keys within hash ``name``"""
        return self.db.hkeys(f"{self.basekey}:{name}")

    def hvals(self, name: str) -> List[str]:
        """Return the list of values within hash ``name``"""
        return self.db.hvals(f"{self.basekey}:{name}")

    def hgetall(self, name: str) -> Dict[str, Any]:
        """Return a Python dict of the hash's name/value pairs"""
        return self.db.hgetall(f"{self.basekey}:{name}")

    def hmset(self, name: str, mapping: dict) -> Any:
        """
        Set key to value within hash ``name`` for each corresponding
        key and value from the ``mapping`` dict.
        """
        return self.db.hmset(f"{self.basekey}:{name}", mapping)
