from discord.ext import commands
import discord
from main import db, app_name

"""
    Utility functions and definitions.
"""


config = f'{app_name}:config:permissions'


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


def supercede(precedent):
    """Decorate a predicate.
    Pass a predicate as param.
    Returns True if either test True."""
    def decorator(predicate):
        def wrapper(ctx):
            if precedent(ctx):
                return True
            return predicate(ctx)
        return wrapper
    return decorator


def require(requisite):
    """Decorate a predicate.
    Pass a predicate as param.
    Returns False if either test False."""
    def decorator(predicate):
        def wrapper(ctx):
            if not requisite(ctx):
                return False
            return predicate(ctx)
        return wrapper
    return decorator


def in_pm(ctx):
    def check():
        return isinstance(
            ctx.channel,
            discord.DMChannel
        ) or isinstance(
            ctx.channel,
            discord.GroupChannel
        )
    return check()


def no_pm(ctx):
    def check():
        return not in_pm(ctx)
    return check()


"""
    These will be internal checks (predicates) for this module.
"""


def bot_owner(ctx):
    def check():
        return ctx.author.id == 125435062127820800
    return check()


@require(no_pm)  # can't have roles in PMs
@supercede(bot_owner)
def has_role(ctx, check):
    """
    Check if someone has a role,
    :param ctx:
    :param check: Prepped find() argument
    :return: Whether or not the role was found
    """
    # Take a prepped find() argument and pass it in
    return discord.utils.find(check, ctx.author.roles) is not None


@supercede(bot_owner)
def sudoer(ctx):
    return ctx.author in db.smembers(f'{config}:sudoers')


@supercede(sudoer)
def admin_perm(ctx):  # TODO: Why didn't this work?
    if ctx.guild:
        return ctx.author.guild_permissions.administrator
    else:
        return False


@supercede(sudoer)
@require(lambda ctx: ctx.guild and ctx.guild.id == 313453805150928906)
def awbw_staff_role(ctx):
    if ctx.guild:
        for role in AWBW_STAFF_ROLES:
            return role in [r.id for r in ctx.author.roles]
    else:
        return False


# @supercede(sudoer)
# def adminrole(ctx):  # TODO: WIP
#     role = db.hget(f'{config}:adminrole', f'{ctx.guild.id}')
#     if role:
#         return has_role(ctx, lambda r: r.id == int(role))
#     else:
#         return False
#
#
# @supercede(sudoer)
# def modrole(ctx):  # TODO: WIP
#     role = db.hget(f'{config}:modrole', f'{ctx.guild.id}')
#     if role:
#         return has_role(ctx, lambda r: r.id == int(role))
#     else:
#         return False


# ### Luc's Predicates ###
#
# def r_pokemon_check(guild):
#     return guild.id == 111504456838819840
#
#
# def r_md_check(guild):
#     return guild.id == 117485575237402630
#
#
# def mod_server_check(guild):
#     return guild.id == 146626123990564864


"""
    The functions that will decorate commands.
"""


def owner():
    def predicate(ctx):
        return bot_owner(ctx)
    return commands.check(predicate)


def sudo():
    def predicate(ctx):
        return sudoer(ctx)
    return commands.check(predicate)


def has_admin():
    def predicate(ctx):
        return admin_perm(ctx)
    return commands.check(predicate)


def awbw_staff():
    def predicate(ctx):
        return awbw_staff_role(ctx)
    return commands.check(predicate)
