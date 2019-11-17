# -*- coding: utf-8 -*-

"""
Mostly stolen from Luc:
    Administrative commands for pory. A lot of them used from my HockeyBot,
    which in turn were mostly from Danny.

Copyright (c) 2015 Rapptz
"""

from importlib import import_module
from os import popen

from asyncio import sleep
from discord.abc import Messageable
from discord.activity import Activity
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.enums import ActivityType, Status
from discord.ext.commands import Cog, command, Context, group
from discord.ext.commands.errors import (
    BadArgument,
    ExtensionAlreadyLoaded,
    ExtensionFailed, ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError
)
from discord.utils import oauth_url

from utils.checks import sudo
from utils.classes import Bot
from utils.utils import SubRedis, GlobalTextChannelConverter


class Admin(Cog):
    """Administrative Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.root_db = bot.db

        self.config = SubRedis(bot.db, f"{bot.APP_NAME}:admin")
        self.config_bot = SubRedis(bot.db, f"{bot.APP_NAME}:config")

        self.say_dest = None
        self.errorlog = bot.errorlog

    """ ######################
         Managing Bot Modules
        ###################### """

    @sudo()
    @group(name="module", aliases=["cog", "mod"], invoke_without_command=True)
    async def module(self, ctx: Context):
        """Base command for managing bot modules

        Use without subcommand to list currently loaded modules"""

        modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
        space = len(max(modules.keys(), key=len))

        fmt = "\n".join([f"{module}{' ' * (space - len(module))} : {cog}" for module, cog in modules.items()])

        em = Embed(
            title="Administration: Currently Loaded Modules",
            description=f"```py\n{fmt}\n```",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @module.command(name="load", usage="(module name)")
    async def load(self, ctx: Context, module: str, verbose: bool = False):
        """load a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"
        msg = None
        verbose_error = None

        try:
            self.bot.load_extension(module)

        except ExtensionNotFound as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error.original

        except ExtensionAlreadyLoaded as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionAlreadyLoaded__**\n"
                            f"Module `{module}` is already loaded",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except NoEntryPointError as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except ExtensionFailed as error:
            if isinstance(error.original, TypeError):
                em = Embed(
                    title="Administration: Load Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"The cog loaded by `{module}` must be a subclass of discord.ext.commands.Cog",
                    color=0xFF0000
                )
            else:
                em = Embed(
                    title="Administration: Load Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"An execution error occurred during module `{module}`'s setup function",
                    color=0xFF0000
                )
            msg = await ctx.send(embed=em)
            verbose_error = error.original

        except Exception as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"{error}",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        else:
            em = Embed(
                title="Administration: Load Module",
                description=f"Module `{module}` loaded successfully",
                color=0x00FF00
            )
            msg = await ctx.send(embed=em)

        finally:
            if verbose and verbose_error:
                await self.errorlog.send(verbose_error, ctx)
            await sleep(5)
            await msg.delete()

    @sudo()
    @module.command(name="unload", usage="(module name)")
    async def unload(self, ctx: Context, module: str, verbose: bool = False):
        """Unload a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"
        msg = None
        verbose_error = None

        try:
            self.bot.unload_extension(module)

        except ExtensionNotLoaded as error:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__ExtensionNotLoaded__**\n"
                            f"Module {module} is not loaded",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except Exception as error:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__{type(error).__name__}__**"
                            f"{error}",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        else:
            em = Embed(
                title="Administration: Unload Module",
                description=f"Module `{module}` unloaded successfully",
                color=0x00FF00
            )
            msg = await ctx.send(embed=em)

        finally:
            if verbose and verbose_error:
                await self.errorlog.send(verbose_error, ctx)
            await sleep(5)
            await msg.delete()

    @sudo()
    @module.command(name="reload", usage="(module name)")
    async def reload(self, ctx: Context, module: str, verbose: bool = False):
        """Reload a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"
        msg = None
        verbose_error = None

        try:
            self.bot.reload_extension(module)

        except ExtensionNotLoaded as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotLoaded__**\n"
                            f"Module {module} is not loaded",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except ExtensionNotFound as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error.original

        except NoEntryPointError as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except ExtensionFailed as error:
            if isinstance(error.original, TypeError):
                em = Embed(
                    title="Administration: Reload Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"The cog loaded by `{module}` must be a subclass of discord.ext.commands.Cog",
                    color=0xFF0000
                )
            else:
                em = Embed(
                    title="Administration: Reload Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"An execution error occurred during module `{module}`'s setup function",
                    color=0xFF0000
                )
            msg = await ctx.send(embed=em)
            verbose_error = error.original

        except Exception as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"{error}",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        else:
            em = Embed(
                title="Administration: Reload Module",
                description=f"Module `{module}` reloaded successfully",
                color=0x00FF00
            )
            msg = await ctx.send(embed=em)

        finally:
            if verbose and verbose_error:
                await self.errorlog.send(verbose_error, ctx)
            await sleep(5)
            await msg.delete()

    @sudo()
    @module.group(name="init", aliases=["initial"], invoke_without_command=True)
    async def init(self, ctx: Context):
        """Get list of modules currently set as initial cogs"""
        init_modules = self.config_bot.lrange("initial_cogs", 0, -1)
        print(type(init_modules))
        str_init_modules = "\n".join(init_modules)
        em = Embed(
            title="Administration: Initial Modules",
            description=f"Modules currently set to be loaded at startup\n```py\n{str_init_modules}\n```",
            color=0x00FF00
        )
        msg = await ctx.send(embed=em)
        await sleep(5)
        await msg.delete()

    @sudo()
    @init.command(name="add", usage="(module name)")
    async def add(self, ctx: Context, module: str, verbose: bool = False):
        """Sets a module to be loaded on startup

        Must be a valid cog with setup function
        Will check with `importlib.import_module` before setting

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        msg = None
        verbose_error = None
        lib = None
        module_setup = None

        init_modules = self.config_bot.lrange("initial_cogs", 0, -1)
        if module in init_modules:
            em = Embed(
                title="Administration: Initial Module Add Failed",
                description=f"**__ExtensionAlreadyLoaded__**\n"
                            f"Module `{module}` is already initial module",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            await sleep(5)
            await msg.delete()
            return

        try:

            # Basic checks for valid cog
            # If we can import it and if it has the setup entry point
            lib = import_module(f"cogs.{module}")
            module_setup = getattr(lib, "setup")

        except ImportError as error:
            em = Embed(
                title="Administration: Initial Module Add Failed",
                description=f"**__ExtensionNotfound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except AttributeError as error:
            em = Embed(
                title="Administration: Initial Module Add Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        except Exception as error:
            em = Embed(
                title="Administration: Initial Module Add Failed",
                description=f"**__{type(error).__name__}__**"
                            f"{error}",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)
            verbose_error = error

        else:
            self.config_bot.lpush("initial_cogs", module)
            em = Embed(
                title="Administration: Initial Module Add",
                description=f"Module `{module}` added to initial modules",
                color=0x00FF00
            )
            msg = await ctx.send(embed=em)

        finally:
            if verbose and verbose_error:
                await self.errorlog.send(verbose_error, ctx)

            # We don't actually need them, so remove
            del lib
            del module_setup

            await sleep(5)
            await msg.delete()

    @sudo()
    @init.command(name="rem", aliases=["del", "delete", "remove"], usage="(module name)")
    async def rem(self, ctx: Context, module: str):
        """Removes a module from initial modules"""

        # Get current list of initial cogs
        init_modules = self.config_bot.lrange("initial_cogs", 0, -1)

        if module in init_modules:
            self.config_bot.lrem("initial_cogs", 0, module)
            em = Embed(
                title="Administration: Initial Module Remove",
                description=f"Module `{module}` added to initial modules",
                color=0x00FF00
            )
            msg = await ctx.send(embed=em)

        else:
            em = Embed(
                title="Administration: Initial Module Remove Failed",
                description=f"Module `{module}` is not an initial module",
                color=0xFF0000
            )
            msg = await ctx.send(embed=em)

        await sleep(5)
        await msg.delete()

    """ ######################
         General Use Commands
        ###################### """

    @sudo()
    @group(name="say", invoke_without_command=True)
    async def say(self, ctx: Context, *, msg: str = ""):
        """Makes the bot send a message

        If self.say_dest is set, it will send the message there
        If it is not, it will send to ctx.channel"""

        dest: Messageable = self.say_dest if self.say_dest else ctx.channel
        await dest.send(msg)

    @sudo()
    @say.command(name="in")
    async def say_in(self, ctx: Context, dest: str = None):
        """Sets the destination for messages from `[p]say`"""

        if dest:
            try:
                self.say_dest: TextChannel = await GlobalTextChannelConverter().convert(ctx, dest)
            except BadArgument as error:
                em = Embed(
                    title="Invalid Channel Identifier",
                    description=f"**__{type(error).__name__}__**: {str(error)}",
                    color=0xFF0000
                )
                await ctx.send(embed=em)
            else:
                em = Embed(
                    title="Administration: Set `say` Destination",
                    description=f"__Say destination set__\n"
                                f"Guild: {self.say_dest.guild.name}\n"
                                f"Channel: {self.say_dest.mention}\n"
                                f"ID: {self.say_dest.id}",
                    color=0x00FF00
                )
                await ctx.send(embed=em)
        else:
            self.say_dest = None
            em = Embed(
                title="Administration: Set `say` Destination",
                description=f"Say destination has been unset",
                color=0x00FF00
            )
            await ctx.send(embed=em)

    @sudo()
    @command(name='invite')
    async def invite(self, ctx: Context):
        em = Embed(
            title=f'OAuth URL for {self.bot.user.name}',
            description=f'[Click Here]'
                        f'({oauth_url(self.bot.app_info.id)}) '
                        f'to invite {self.bot.user.name} to your guild.',
            color=ctx.guild.me.colour
        )
        await ctx.send(embed=em)

    """ ###############################################
         Change Custom Status Message and Online State
        ############################################### """

    @sudo()
    @group(name='status', invoke_without_command=True)
    async def status(self, ctx: Context):
        """Changes the status and state"""
        pass

    @sudo()
    @status.command(name="online")
    async def online(self, ctx: Context):
        """Changes online status to Online"""
        await self.bot.change_presence(status=Status.online)

        em = Embed(
            title="Administration: Change Online Status",
            description="Status changed to `online`",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="dnd", aliases=["do_not_disturb"])
    async def dnd(self, ctx: Context):
        """Changes online status to Do Not Disturb"""
        await self.bot.change_presence(status=Status.dnd)

        em = Embed(
            title="Administration: Change Online Status",
            description="Status changed to `dnd`",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="idle")
    async def idle(self, ctx: Context):
        """Changes online status to Idle"""
        await self.bot.change_presence(status=Status.idle)

        em = Embed(
            title="Administration: Change Online Status",
            description="Status changed to `idle`",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="invisible", aliases=["offline"])
    async def invisible(self, ctx: Context):
        """Changes online status to Invisible"""
        await self.bot.change_presence(status=Status.invisible)

        em = Embed(
            title="Administration: Change Online Status",
            description="Status changed to `invisible`",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="remove", aliases=["rem", "del", "delete", "stop"])
    async def remove(self, ctx: Context):
        """Removes status message"""
        activity = Activity(name=None)
        await self.bot.change_presence(activity=activity)

        em = Embed(
            title="Administration: Status Message Removed",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="playing", aliases=["game"])
    async def playing(self, ctx: Context, *, status: str):
        """Changes status to `Playing (status)`

        Will also change status header to `Playing A Game`"""
        activity = Activity(name=status, type=ActivityType.playing)
        await self.bot.change_presence(activity=activity)

        em = Embed(
            title="Administration: Status Message Set",
            description=f"**Playing A Game\n**"
                        f"Playing {status}",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="streaming")
    async def streaming(self, ctx: Context, *, status: str):
        """Changes status to `Playing (status)`

        Will also change status header to `Live on Twitch`"""
        activity = Activity(name=status, type=ActivityType.streaming)
        await self.bot.change_presence(activity=activity)

        em = Embed(
            title="Administration: Status Message Set",
            description=f"**Live On Twitch\n**"
                        f"Playing {status}",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="listening")
    async def listening(self, ctx: Context, *, status: str):
        """Changes status to `Listening to (status)`"""
        activity = Activity(name=status, type=ActivityType.listening)
        await self.bot.change_presence(activity=activity)

        em = Embed(
            title="Administration: Status Message Set",
            description=f"Listening to {status}",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @status.command(name="watching")
    async def watching(self, ctx: Context, *, status: str):
        """Changes status to `Watching (status)`"""
        activity = Activity(name=status, type=ActivityType.watching)
        await self.bot.change_presence(activity=activity)

        em = Embed(
            title="Administration: Status Message Set",
            description=f"Watching {status}",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    """ #########################
         Updating and Restarting
        ######################### """

    @staticmethod
    def gitpull() -> str:
        """Uses os.popen to `git pull`"""
        resp = popen("git pull").read()
        resp = f"```diff\n{resp}\n```"
        return resp

    @sudo()
    @command(name="pull")
    async def pull(self, ctx: Context):
        """Updates bot repo from master"""

        em = Embed(
            title="Administration: Git Pull",
            description=self.gitpull(),
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @sudo()
    @group(name='restart', aliases=["kill", "f"], invoke_without_command=True)
    async def _restart(self, ctx: Context):
        """Restarts the bot"""

        em = Embed(
            title="Administration: Restart",
            description=f"{ctx.author.mention} initiated bot restart.",
            color=0x00FF00
        )

        await ctx.send(embed=em)
        await self.bot.logout()

    @sudo()
    @_restart.command(name="pull")
    async def restart_pull(self, ctx: Context):
        """Updates repo from origin master and restarts"""

        em = Embed(
            title="Administration: Git Pull and Restart",
            description=f"{ctx.author.mention} initiated bot code update and restart.\n{self.gitpull()}",
            color=0x00FF00
        )

        await ctx.send(embed=em)
        await self.bot.logout()


def setup(bot: Bot):
    bot.add_cog(Admin(bot))
