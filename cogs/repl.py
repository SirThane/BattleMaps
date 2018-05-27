"""Cog to provide REPL-like functionality"""

import inspect
import sys
from contextlib import contextmanager
from io import StringIO

import discord
from discord.ext import commands
from .utils import checks, utils


MD = "```py\n{0}\n```"


@contextmanager
def stdoutio(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class REPL:
    """Read-Eval-Print Loop debugging commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.ret = None
        self._env_store = {}
        self.emb_pag = utils.Paginator(
            page_limit=1014,
            trunc_limit=1850,
            header_extender='Cont.'
        )

    def emb_dict(self, title: str, desc: str) -> dict:
        d = {
            "title": title,
            "description": desc,
            "fields": []
        }
        return d

    def _env(self, ctx):
        import random
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'discord': discord,
            'random': random,
            'ret': self.ret,
        }
        env.update(globals())
        env.update(self._env_store)
        return env

    @checks.sudo()
    @commands.group(hidden=True, name='env')
    async def env(self, ctx: commands.Context) -> None:
        pass

    @checks.sudo()
    @env.command(
        hidden=True,
        name='update',
        aliases=['store', 'add', 'append']
    )
    async def _update(self, ctx: commands.Context, name: str) -> None:
        if name:
            self._env_store[name] = self.ret
            emb = discord.Embed(
                title='Environment Updated',
                color=discord.Colour.green()
            )
            emb.add_field(
                name=name,
                value=repr(self.ret)
            )
        else:
            emb = discord.Embed(
                title='Environment Update',
                description='You must enter a name',
                color=discord.Colour.red()
            )
        await ctx.send(embed=emb)

    @checks.sudo()
    @env.command(
        hidden=True,
        name='remove',
        aliases=['rem', 'del', 'pop']
    )
    async def _remove(self, ctx: commands.Context, name: str) -> None:
        if name:
            v = self._env_store.pop(name, None)
        else:
            v = None
            name = 'You must enter a name'
        if v:
            emb = discord.Embed(
                title='Environment Item Removed',
                color=discord.Colour.green()
            )
            emb.add_field(
                name=name,
                value=repr(v)
            )
        else:
            emb = discord.Embed(
                title='Environment Item Not Found',
                description=name,
                color=discord.Colour.red()
            )
        await ctx.send(embed=emb)

    @checks.sudo()
    @env.command(hidden=True, name='list')
    async def _list(self, ctx: commands.Context) -> None:
        if len(self._env_store.keys()):
            emb = discord.Embed(
                title='Environment Store List',
                color=discord.Colour.green()
            )
            for k, v in self._env_store.items():
                emb.add_field(
                    name=k,
                    value=repr(v)
                )
        else:
            emb = discord.Embed(
                title='Environment Store List',
                description='Environment Store is currently empty',
                color=discord.Colour.green()
            )
        await ctx.send(embed=emb)

    @checks.sudo()
    @commands.command(hidden=True, name='await')
    async def _await(self, ctx: commands.Context, *, code: str) -> None:

        try:
            resp = eval(code, self._env(ctx))
            if inspect.isawaitable(resp):
                await resp
            else:
                raise Exception("Not awaitable.")
        except Exception as e:
            await ctx.send(str(e))
        finally:
            await ctx.message.delete()

    @checks.sudo()
    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx: commands.Context, *, code: str) -> None:
        """Run eval() on an input."""

        code = code.strip('` ')
        emb = self.emb_dict(
            title='Eval on',
            desc=MD.format(code)
        )

        try:
            result = eval(code, self._env(ctx))
            if inspect.isawaitable(result):
                result = await result
            self.ret = result
            self.emb_pag.set_headers(['Yielded result:'])
            emb['color'] = 0x00FF00
            for h, v in self.emb_pag.paginate(result):
                field = {
                    'name': h,
                    'value': MD.format(v),
                    'inline': False
                }
                emb['fields'].append(field)

        except Exception as e:
            emb['color'] = 0xFF0000
            field = {
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': '{0}'.format(e),
                'inline': False
            }
            emb['fields'].append(field)

        embed = discord.Embed().from_data(emb)

        await ctx.message.delete()
        await ctx.channel.send(embed=embed)

    @checks.sudo()
    @commands.command(hidden=True, name='exec')
    async def _exec(self, ctx: commands.Context, *, code: str) -> None:
        """Run exec() on an input."""

        code = code.strip('```\n ')
        emb = self.emb_dict(title='Exec on', desc=MD.format(code))

        try:
            with stdoutio() as s:
                exec(code, self._env(ctx))
                result = str(s.getvalue())
            self.emb_pag.set_headers(['Yielded result:'])
            emb['color'] = 0x00FF00
            for h, v in self.emb_pag.paginate(result):
                field = {
                    'name': h,
                    'value': MD.format(v),
                    'inline': False,
                }
                emb['fields'].append(field)
        except Exception as e:
            emb['color'] = 0xFF0000
            field = {
                'inline': False,
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': str(e)
            }
            emb['fields'].append(field)

        embed = discord.Embed().from_data(emb)

        await ctx.message.delete()
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(REPL(bot))
