"""System for user-created polls"""

# Site
from discord.channel import TextChannel
from discord.colour import Color
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import check, group, has_guild_permissions
from discord.ext.menus import button, First, Last, Menu
from discord.raw_models import RawReactionActionEvent
from discord.role import Role

# Local
from main import APP_NAME, db
from utils.classes import Bot, Embed, SubRedis


def has_permission(ctx: Context):
    allowed_roles = db.smembers(f"{APP_NAME}:poll:allowed_roles:{ctx.guild.id}")
    allowed_roles = [int(role_id) for role_id in allowed_roles]
    return any((
        role.id in allowed_roles for role in ctx.author.roles
    ))


class Confirm(Menu):

    class Buttons:
        yes = b"\xE2\x9C\x85".decode("utf8")  # ✅  :white_check_mark:
        no  = b"\xE2\x9D\x8C".decode("utf8")  # ❌  :x:

    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)

    @button(Buttons.yes, position=First(0))
    async def choice_yes(self, payload: RawReactionActionEvent):
        pass

    @button(Buttons.yes, position=Last(0))
    async def choice_yes(self, payload: RawReactionActionEvent):
        pass


class Poll(Cog):
    """User-created polls"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = SubRedis(bot.db, "poll")

        self.errorlog = bot.errorlog

    @check(has_permission)
    @group(name="poll", invoke_without_command=True)
    async def poll(self, ctx: Context):
        await ctx.send("Placeholder")

    """ #######
         Setup
        ####### """

    @check(has_permission)
    @poll.command(name="view")
    async def view(self, ctx: Context):
        pass

    @check(has_permission)
    @poll.command(name="create", aliases=["new"])
    async def create(self, ctx: Context, *, name: str):
        pass

    @check(has_permission)
    @poll.command(name="discard", aliases=["drop"])
    async def discard(self, ctx: Context):
        pass

    @check(has_permission)
    @poll.command(name="name", aliases=["title"])
    async def name(self, ctx: Context):
        pass

    @check(has_permission)
    @poll.command(name="add_option", aliases=["add"])
    async def add_option(self, ctx: Context):
        pass

    @check(has_permission)
    @poll.command(name="remove_option", aliases=["remove", "delete_option", "delete", "rem", "del"])
    async def remove_option(self, ctx: Context):
        pass

    """ #########
         Running
        ######### """

    @check(has_permission)
    @poll.command(name="start")
    async def start(self, ctx: Context, *, channel: TextChannel):
        pass

    @check(has_permission)
    @poll.command(name="view")
    async def view(self, ctx: Context):
        pass

    """ ################
         Administrative
        ################ """

    @has_guild_permissions(manage_guild=True)
    @poll.command(name="add_role", hidden=True)
    async def add_role(self, ctx: Context, role: Role):

        if self.config.sismember(f"allowed_roles:{ctx.guild.id}", role.id):
            em = Embed(
                title="Polls Administration",
                description=f"{role.mention} is already allowed to conduct polls.",
                color=Color.red()
            )
            await ctx.send(embed=em, delete_after=5)

        else:
            self.config.sadd(f"allowed_roles:{ctx.guild.id}", role.id)
            em = Embed(
                title="Polls Administration",
                description=f"{role.mention} is now allowed to conduct polls.",
                color=Color.green()
            )
            await ctx.send(embed=em, delete_after=5)

    @has_guild_permissions(manage_guild=True)
    @poll.command(name="remove_role", aliases=["rem_role"], hidden=True)
    async def remove_role(self, ctx: Context, role: Role):

        if self.config.sismember(f"allowed_roles:{ctx.guild.id}", role.id):
            self.config.srem(f"allowed_roles:{ctx.guild.id}", role.id)
            em = Embed(
                title="Polls Administration",
                description=f"{role.mention} is no longer allowed to conduct polls.",
                color=Color.green()
            )
            await ctx.send(embed=em, delete_after=5)

        else:
            em = Embed(
                title="Polls Administration",
                description=f"{role.mention} is not allowed to conduct polls.",
                color=Color.red()
            )
            await ctx.send(embed=em, delete_after=5)

    @has_guild_permissions(manage_guild=True)
    @poll.command(name="list_roles", aliases=["roles"], hidden=True)
    async def list_roles(self, ctx: Context):
        role_ids = sorted(self.config.smembers(f"allowed_roles:{ctx.guild.id}"))

        if role_ids:
            roles = "\n".join([ctx.guild.get_role(int(role_id)).mention for role_id in role_ids])
            em = Embed(
                title="Polls Administration",
                description=f"The following roles are allowed to conduct polls:\n{roles}",
                color=Color.green()
            )
            await ctx.send(embed=em, delete_after=5)

        else:
            em = Embed(
                title="Polls Administration",
                description="There are currently no roles allowed to conduct polls.",
                color=Color.red()
            )
            await ctx.send(embed=em, delete_after=5)


def setup(bot: Bot):
    """Poll"""
    bot.add_cog(Poll(bot))
