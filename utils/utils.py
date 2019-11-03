"""Utility functions and classes.
"""

import sys
from contextlib import contextmanager
from io import StringIO
from traceback import extract_tb

import redis
from discord import Colour, DiscordException, Embed
from discord.ext.commands import Context
from typing import Any, Generator, Iterable, List, Tuple, Union


ZWSP = u'\u200b'


async def em_tb(error: Union[Exception, DiscordException], ctx: Context = None):
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
            "value": f"Line `{ln}` of `{func}`:\n```py\n{txt}\n```",
            "inline": False
        } for fn, ln, func, txt in stack
    ]

    em = Embed(
        color=Colour.red(),
        title=title,
        description=f"{description}"
    )

    for field in tb_fields:
        em.add_field(**field)

    return em


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


def fold_list(l: Iterable, width: int) -> Generator[List[Any], None, None]:
    l = list(l)
    try:
        assert len(l) % width == 0
    except AssertionError:
        raise ValueError(f"Width must be factor of list length ({len(l)}")
    for i in range(0, len(l), width):
        yield l[i:i + width]


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


class StrictRedis(redis.StrictRedis):
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
