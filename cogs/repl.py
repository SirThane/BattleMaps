"""Cog to provide REPL-like functionality"""

# Lib
from asyncio.tasks import sleep
from inspect import isawaitable

# Site
from discord.colour import Colour
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command, group

# Local
from utils.classes import Bot, Embed
from utils.checks import sudo
# from utils.utils import stdoutio

MD = "```py\n{0}\n```"


class REPL(Cog):
    """Read-Eval-Print Loop debugging commands"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = bot.db
        self.config = f"{bot.APP_NAME}:REPL"

        self.errorlog = bot.errorlog

        self.ret = None
        self._env_store = dict()

    def _env(self, ctx: Context) -> dict:
        import discord
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
            'db': self.db,
            'ret': self.ret,
        }
        env.update(globals())
        env.update(self._env_store)
        return env

    @sudo()
    @group(name='env')
    async def env(self, ctx: Context):
        if len(self._env_store):
            emb = Embed(title='Environment Store List', color=Colour.green())
            for k, v in self._env_store.items():
                emb.add_field(name=k, value=repr(v))
        else:
            emb = Embed(
                title='Environment Store List',
                description='Environment Store is currently empty',
                color=Colour.green()
            )
        await ctx.send(embed=emb)

    @sudo()
    @env.command(name='update', aliases=['store', 'add', 'append'])
    async def _update(self, ctx: Context, name: str):
        """Add `ret` as a new object to custom REPL environment"""

        if name:
            self._env_store[name] = self.ret
            em = Embed(title='Environment Updated', color=Colour.green())
            em.add_field(name=name, value=repr(self.ret))

        else:
            em = Embed(
                title='Environment Update',
                description='You must enter a name',
                color=Colour.red()
            )

        await ctx.send(embed=em)

    @sudo()
    @env.command(name='remove', aliases=['rem', 'del', 'pop'])
    async def _remove(self, ctx: Context, name: str):
        if name:
            v = self._env_store.pop(name, None)
        else:
            v = None
            name = 'You must enter a name'

        if v:
            em = Embed(title='Environment Item Removed', color=Colour.green())
            em.add_field(name=name, value=repr(v))
        else:
            em = Embed(
                title='Environment Item Not Found',
                description=name,
                color=Colour.red()
            )
        await ctx.send(embed=em)

    @sudo()
    @command(hidden=True, name='eval')
    async def _eval(self, ctx: Context, *, code: str) -> None:
        """Run eval() on an input."""

        code = code.strip('` ')

        try:
            result = eval(code, self._env(ctx))
            if isawaitable(result):
                result = await result
            self.ret = result
            em = Embed(title='Eval on', description=MD.format(code), color=0x00FF00)
            em.add_field(name="Result:", value=MD.format(result), inline=False)

        except Exception as e:
            em = Embed(title='Eval on', desc=MD.format(code), color=0xFF0000)
            em.add_field(name=f"Exception: {e.__name__}", value=str(e), inline=False)

        for page in em.split():
            await ctx.send(embed=page)
            await sleep(0.1)

    # @sudo()
    # @command(hidden=True, name='exec')
    # async def _exec(self, ctx: Context, *, code: str) -> None:
    #     """Run exec() on an input."""
    #
    #     code = code.strip('```\n ')
    #     emb = self.emb_dict(title='Exec on', desc=MD.format(code))
    #
    #     try:
    #         with stdoutio() as s:
    #             exec(code, self._env(ctx))
    #             result = str(s.getvalue())
    #         self.emb_pag.set_headers(['Yielded result:'])
    #         emb['colour'] = 0x00FF00
    #         for h, v in self.emb_pag.paginate(result):
    #             field = {
    #                 'name': h,
    #                 'value': MD.format(v),
    #                 'inline': False,
    #             }
    #             emb['fields'].append(field)
    #     except Exception as e:
    #         emb['colour'] = 0xFF0000
    #         field = {
    #             'inline': False,
    #             'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
    #             'value': str(e)
    #         }
    #         emb['fields'].append(field)
    #
    #     embed = Embed().from_dict(emb)
    #
    #     await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """REPL"""
    bot.add_cog(REPL(bot))
