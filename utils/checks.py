
# Lib
from typing import Callable

# Site
from discord.channel import DMChannel, GroupChannel
from discord.ext.commands.context import Context
from discord.ext.commands.core import check
from discord.utils import find

# Local
from main import db, APP_NAME


"""
    Utility functions and definitions.
"""


config = f'{APP_NAME}:config:permissions'


AWBW_GOD_ROLE = 345549110528704513
AWBW_DEMIGOD_ROLE = 397475020076744704
AWBW_CHAN_MOD_ROLE = 314798536837562378
AWBW_MC_ROLE = 324122288930684928
AWBW_WIKI_MOD_ROLE = 392397509714116618

AWBW_STAFF_ROLES = [
    AWBW_GOD_ROLE,
    AWBW_DEMIGOD_ROLE,
    AWBW_CHAN_MOD_ROLE,
    AWBW_MC_ROLE,
    AWBW_WIKI_MOD_ROLE,
]


def supercede(precedent: Callable) -> Callable:
    """Decorate a predicate.
    Pass a predicate as param.
    Returns True if either test True."""
    def decorator(predicate: Callable) -> Callable:
        def wrapper(ctx: Context) -> bool:
            return precedent(ctx) or predicate(ctx)
        return wrapper
    return decorator


def require(requisite: Callable) -> Callable:
    """Decorate a predicate.
    Pass a predicate as param.
    Returns False if either test False."""
    def decorator(predicate: Callable) -> Callable:
        def wrapper(ctx: Context) -> bool:
            return predicate(ctx) and requisite(ctx)
        return wrapper
    return decorator


def in_pm(ctx: Context) -> bool:
    def chk() -> bool:
        return isinstance(ctx.channel, DMChannel) or isinstance(ctx.channel, GroupChannel)
    return chk()


def no_pm(ctx: Context) -> bool:
    def chk() -> bool:
        return not in_pm(ctx)
    return chk()


"""
    These will be internal checks (predicates) for this module.
"""


def bot_owner(ctx: Context) -> bool:
    def chk() -> bool:
        return ctx.author.id == 125435062127820800
    return chk()


@require(no_pm)  # can't have roles in PMs
@supercede(bot_owner)
def has_role(ctx: Context, chk) -> bool:  # TODO: What type is chk?
    """
    Check if someone has a role,
    :param ctx:
    :param chk: Prepped find() argument
    :return: Whether or not the role was found
    """
    # Take a prepped find() argument and pass it in
    return find(chk, ctx.author.roles) is not None


@supercede(bot_owner)
def sudoer(ctx: Context) -> bool:
    return ctx.author in db.smembers(f'{config}:sudoers')


@supercede(sudoer)
def admin_perm(ctx: Context) -> bool:  # TODO: Why didn't this work?
    if ctx.guild:
        return ctx.author.guild_permissions.administrator
    else:
        return False


@supercede(sudoer)
@require(lambda ctx: ctx.guild and ctx.guild.id == 313453805150928906)
def awbw_staff_role(ctx: Context) -> bool:
    if ctx.guild:
        for role in AWBW_STAFF_ROLES:
            return role in [r.id for r in ctx.author.roles]
    else:
        return False


"""
    The functions that will decorate commands.
"""


def owner():
    def predicate(ctx: Context) -> bool:
        return bot_owner(ctx)
    return check(predicate)


def sudo():
    def predicate(ctx: Context) -> bool:
        return sudoer(ctx)
    return check(predicate)


def has_admin():
    def predicate(ctx: Context) -> bool:
        return admin_perm(ctx)
    return check(predicate)


def awbw_staff():
    def predicate(ctx):
        return awbw_staff_role(ctx)
    return check(predicate)
