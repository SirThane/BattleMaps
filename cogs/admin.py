"""
Mostly stolen from Luc:
    Administrative commands for pory. A lot of them used from my HockeyBot,
    which in turn were mostly from Danny.

Copyright (c) 2015 Rapptz
"""

import os
import sys
import traceback
from asyncio import sleep
from contextlib import contextmanager
from io import StringIO

from discord import Embed, Game
from discord.ext.commands import Cog, command, Context
from discord.utils import oauth_url

from cogs.utils.classes import Bot
from cogs.utils import checks


@contextmanager
def stdoutio(stdout=None):  # TODO: Refactor this for out and err
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class Admin(Cog):
    """Administrative Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = bot.db
        self.config = f"{bot.APP_NAME}:admin"

    @checks.sudo()
    @command(name="load")
    async def load(self, ctx: Context, *, cog: str, verbose: bool = False):
        """load a module"""
        cog = f"cogs.{cog}"
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            if not verbose:
                await ctx.send(content='{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.send(content=traceback.print_tb(e.__traceback__))
        else:
            await ctx.send(content="Module loaded successfully.")

    @checks.sudo()
    @command(name="unload")
    async def unload(self, ctx: Context, *, cog: str):
        """Unload a module"""

        cog = f"cogs.{cog}"
        msg = None

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            msg = await ctx.send(
                embed=Embed(
                    title="Administration: Unload Cog Failed",
                    description=f"{type(e).__name__}: {e}",
                    color=0xFF0000
                )
            )
        else:
            msg = await ctx.send(
                embed=Embed(
                    title="Administration",
                    description=f"Module `{cog}` unloaded successfully",
                    color=0x00FF00
                )
            )
            await sleep(5)
        finally:
            await msg.delete()

    @checks.sudo()
    @command(hidden=True)
    async def reload(self, ctx: Context, *, cog: str):
        """Reloads a module."""
        cog = f"cogs.{cog}"
        try:
            self.bot.unload_extension(cog)
            await sleep(1)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send(content='Module reloaded.')

    @checks.sudo()
    @command(name="say_in", hidden=True)
    async def say_in(self, ctx, ch_id: int, *, msg: str = ""):
        channel = self.bot.get_channel(ch_id)
        if channel:
            await channel.send(msg)
        else:
            ctx.author.send(f"Couldn't find channel {ch_id}.")

    @checks.sudo()
    @command(name='invite', hidden=True, enabled=False)
    async def invite(self, ctx: Context):
        em = Embed(
            title=f'OAuth URL for {self.bot.user.name}',
            description=f'[Click Here]'
                        f'({oauth_url(self.bot.app_info.id)}) '
                        f'to invite {self.bot.user.name} to your guild.',
            color=ctx.guild.me.color
        )
        await ctx.send(embed=em)

    @checks.sudo()
    @command(name='game', hidden=True)
    async def game(self, ctx: Context, *, game: str = None):
        """Changes status to 'Playing <game>'.
        Command without argument will remove status.

        `[p]game <string>`"""
        if game:
            await self.bot.change_presence(activity=Game(name=game))
        else:
            await self.bot.change_presence(activity=Game(name=game))
        await ctx.message.edit('Presence updated.')
        await sleep(5)
        await ctx.message.delete

    """ It might be cool to make some DB altering commands. """

    @staticmethod
    def _pull() -> str:
        resp = os.popen("git pull").read()
        resp = f"```diff\n{resp}\n```"
        return resp

    @checks.sudo()
    @command(name="pull", hidden=True)
    async def pull(self, ctx: Context):
        await ctx.send(embed=Embed(title="Git Pull", description=self._pull(), color=0x00FF00))

    @checks.sudo()
    @command(hidden=True, name='restart', aliases=["kill", "f"])
    async def _restart(self, ctx: Context, *, arg: str = None):  # Overwrites builtin kill()
        if arg and arg.lower() == "pull":
            resp = self._pull()
        else:
            resp = ""
        await ctx.send(content=f"{resp}\nRestarting by command. . .")
        await self.bot.logout()


def setup(bot: Bot):
    bot.add_cog(Admin(bot))
