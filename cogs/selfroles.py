
# Lib
from asyncio import sleep

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.converter import RoleConverter
from discord.ext.commands.core import command, group, guild_only
from discord.ext.commands.errors import BadArgument

# Local
from utils.classes import Bot, Embed, SubRedis
from utils.checks import awbw_staff


ROLE_SHORTNAME = {
    'os': 424524133670453250,
    'bm': 424524139999789058,
    'ge': 424524144353476629,
    'yc': 424524148958560266,
    'bh': 424524153387876353,
    'rf': 424541540740890624,
    'gs': 424541543810990089,
    'bd': 424541547757961216,
    'ab': 424541550853488640,
    'js': 424541553898291200,
    'ci': 424541559766122518,
    'pc': 424541563520024576,
    'tg': 424541566934319104,
    'pl': 424541571300589587,
    'ar': 455439202692366367,
    'wn': 455439210883842048
}


class SelfRoles(Cog):
    """Commands for managing and assigning selfroles"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = SubRedis(bot.db, "selfroles")

        self.errorlog = bot.errorlog

        self._selfroles = {g.id: [] for g in bot.guilds}

        for key in self.config.scan_iter(match=f"{self.config}:*"):
            guild = bot.get_guild(int(key.split(":")[-1]))
            if not guild:
                continue
            self._selfroles[guild.id] = []
            r_ids = [int(r_id) for r_id in self.config.smembers(key)]
            for role in guild.roles:
                if role.id in r_ids:
                    self._selfroles[guild.id].append(role.id)

    @guild_only()
    @command(name="iam")
    async def iam(self, ctx: Context, *, role) -> None:
        """Add a self-assignable role

        If the `role` is configured as an assignable
        selfrole, you can use this command to assign
        the role to yourself.

        `[p]iam role`
        `[p]iam @role`
        `[p]iam role id`

        You can also use a country's short code.
        e.g. `[p]iam os`"""

        if role.lower() in ROLE_SHORTNAME.keys():
            role = str(ROLE_SHORTNAME[role.lower()])

        try:
            role = await RoleConverter().convert(ctx, role)

        except BadArgument:
            await ctx.send(
                embed=Embed(
                    color=ctx.guild.me.colour,
                    title="⚠ Selfroles",
                    description=f"Could not recognize role."
                )
            )

        else:
            if role in ctx.author.roles:
                await ctx.send(
                    embed=Embed(
                        color=ctx.guild.me.colour,
                        title="⚠ Selfroles",
                        description="You already have this role assigned."
                    )
                )
            elif role.id in self._selfroles.get(ctx.guild.id):
                for author_role in ctx.author.roles:
                    if author_role.id in self._selfroles[ctx.guild.id]:
                        await ctx.author.remove_roles(
                            author_role,
                            reason=ctx.message.content,
                            atomic=True
                        )
                        await sleep(0.5)
                await ctx.author.add_roles(
                    role,
                    reason=ctx.message.content,
                    atomic=True
                )
                await ctx.send(
                    embed=Embed(
                        color=role.colour,
                        title="Role Assigned",
                        description=f"Congratulations, {ctx.author.mention}!"
                                    f" You now have the **{role.mention}** "
                                    f"role."
                    )
                )
            else:
                await ctx.send(
                    embed=Embed(
                        color=0xFF0000,
                        title="⚠ Selfroles",
                        description="That role is not self-assignable."
                    )
                )

    @guild_only()
    @group(name="selfroles", aliases=["selfrole"], invoke_without_command=True)
    async def selfroles(self, ctx: Context):
        """View all selfroles"""

        r_ids = self._selfroles.get(ctx.guild.id)

        if r_ids:
            roles = []
            for role in ctx.guild.roles:
                if role.id in r_ids:
                    roles.append(role.mention)

            roles = "\n".join(roles)

            await ctx.send(
                embed=Embed(
                    color=ctx.guild.me.colour,
                    title="Selfroles",
                    description=f"The following roles are self-assignable:\n"
                                f"{roles}"
                                f"\n"
                                f"\n"
                                f"See `?help iam` for assigning selfroles."
                )
            )

        else:
            await ctx.send(
                embed=Embed(
                    color=ctx.guild.me.colour,
                    title="Selfroles",
                    description="There are currently no assignable selfroles.\n"
                                "Staff may configure selfroles with `?selfrole add`."
                )
            )

    @awbw_staff()
    @selfroles.command(name="add")
    async def _add(self, ctx: Context, *, role) -> None:
        """Configures a role as a selfrole"""

        r_ids = [i for i in self._selfroles.get(ctx.guild.id)]

        try:
            role = await RoleConverter().convert(ctx, role)
        except BadArgument:
            await ctx.send(
                embed=Embed(
                    color=ctx.guild.me.colour,
                    title="⚠ Selfroles Management",
                    description=f"Could not recognize role."
                )
            )
        else:
            if role.id in r_ids:
                await ctx.send(
                    embed=Embed(
                        color=ctx.guild.me.colour,
                        title="⚠ Selfroles Management",
                        description=f"Role {role.mention} is already configured as a selfrole."
                    )
                )
            else:
                self.config.sadd(f"{self.config}:{ctx.guild.id}", str(role.id))
                self._selfroles[ctx.guild.id].append(role.id)
                await ctx.send(
                    embed=Embed(
                        color=ctx.guild.me.colour,
                        title="Selfroles Management",
                        description=f"Role {role.mention} has been added to selfroles."
                    )
                )

    @awbw_staff()
    @selfroles.command(name="rem", aliases=["del", "remove", "delete"])
    async def _rem(self, ctx: Context, *, role):
        """Removes a role from selfroles"""

        r_ids = [i for i in self._selfroles.get(ctx.guild.id)]

        try:
            role = await RoleConverter().convert(ctx, role)

        except BadArgument:
            await ctx.send(
                embed=Embed(
                    color=ctx.guild.me.colour,
                    title="⚠ Selfroles Management",
                    description=f"Could not recognize role."
                )
            )

        else:
            if role.id in r_ids:
                self.config.srem(f"{self.config}:{ctx.guild.id}", role.id)
                self._selfroles[ctx.guild.id].remove(role.id)
                await ctx.send(
                    embed=Embed(
                        color=ctx.guild.me.colour,
                        title="Selfroles Management",
                        description=f"Role {role.mention} has been removed  from selfroles."
                    )
                )
            else:
                await ctx.send(
                    embed=Embed(
                        color=ctx.guild.me.colour,
                        title="⚠ Selfroles Management",
                        description=f"Role {role.mention} is not configured as a selfrole."
                    )
                )


def setup(bot: Bot):
    """SelfRoles"""
    bot.add_cog(SelfRoles(bot))
