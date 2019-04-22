
from asyncio import sleep
import discord
from discord.ext import commands
from cogs.utils import checks


class SelfRoles:

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.config = f"{bot.APP_NAME}:selfroles"
        self._selfroles = {g.id: [] for g in bot.guilds}

        for key in self.db.scan_iter(match=f"{self.config}:*"):
            guild = bot.get_guild(int(key.split(":")[-1]))
            if not guild:
                continue
            self._selfroles[guild.id] = []
            r_ids = [int(r_id) for r_id in self.db.smembers(key)]
            for role in guild.roles:
                if role.id in r_ids:
                    self._selfroles[guild.id].append(role.id)

    @commands.command(name="iam")
    async def iam(self, ctx: commands.Context, *, role) -> None:
        """Add a self-assignable role

        If the `role` is configured as an assignable
        selfrole, you can use this command to assign
        the role to yourself.

        `[p]iam role`
        `[p]iam @role`
        `[p]iam role id`"""

        try:
            role = await commands.RoleConverter().convert(ctx, role)

        except commands.errors.BadArgument:
            await ctx.send(
                embed=discord.Embed(
                    color=ctx.guild.me.color,
                    title="⚠ Selfroles",
                    description=f"Could not recognize role."
                )
            )

        else:
            if role in ctx.author.roles:
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.guild.me.color,
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
                    embed=discord.Embed(
                        color=role.color,
                        title="Role Assigned",
                        description=f"Congratulations, {ctx.author.mention}!"
                                    f" You now have the **{role.mention}** "
                                    f"role."
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        color=0xFF0000,
                        title="⚠ Selfroles",
                        description="That role is not self-assignable."
                    )
                )

    @commands.group(name="selfroles", aliases=["selfrole"],
                    invoke_without_command=True)
    async def selfroles(self, ctx: commands.Context):
        """View all selfroles"""

        r_ids = self._selfroles.get(ctx.guild.id)

        if r_ids:
            roles = []
            for role in ctx.guild.roles:
                if role.id in r_ids:
                    roles.append(role.mention)

            roles = "\n".join(roles)

            await ctx.send(
                embed=discord.Embed(
                    color=ctx.guild.me.color,
                    title="Selfroles",
                    description=f"The following roles are self-assignable:\n"
                                f"{roles}\n\nSee `help $$iam` for assigning "
                                f"selfroles."
                )
            )

        else:
            await ctx.send(
                embed=discord.Embed(
                    color=ctx.guild.me.color,
                    title="Selfroles",
                    description="There are currently no assignable selfroles."
                                "\nStaff may configure selfroles with `$$"
                                "selfrole add`."
                )
            )

    @checks.awbw_staff()
    @selfroles.command(name="add")
    async def _add(self, ctx: commands.Context, *, role) -> None:
        """Configures a role as a selfrole"""

        r_ids = [i for i in self._selfroles.get(ctx.guild.id)]

        try:
            role = await commands.RoleConverter().convert(ctx, role)
        except commands.errors.BadArgument:
            await ctx.send(
                embed=discord.Embed(
                    color=ctx.guild.me.color,
                    title="⚠ Selfroles Management",
                    description=f"Could not recognize role."
                )
            )
        else:
            if role.id in r_ids:
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.guild.me.color,
                        title="⚠ Selfroles Management",
                        description=f"Role {role.mention} is already "
                                    f"configured as a selfrole."
                    )
                )
            else:
                self.db.sadd(f"{self.config}:{ctx.guild.id}", str(role.id))
                self._selfroles[ctx.guild.id].append(role.id)
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.guild.me.color,
                        title="Selfroles Management",
                        description=f"Role {role.mention} has been added to "
                                    f"selfroles."
                    )
                )

    @checks.awbw_staff()
    @selfroles.command(name="rem", aliases=["del", "remove", "delete"])
    async def _rem(self, ctx: commands.Context, *, role) -> None:
        """Removes a role from selfroles"""

        r_ids = [i for i in self._selfroles.get(ctx.guild.id)]

        try:
            role = await commands.RoleConverter().convert(ctx, role)

        except commands.errors.BadArgument:
            await ctx.send(
                embed=discord.Embed(
                    color=ctx.guild.me.color,
                    title="⚠ Selfroles Management",
                    description=f"Could not recognize role."
                )
            )

        else:
            if role.id in r_ids:
                self.db.srem(f"{self.config}:{ctx.guild.id}", role.id)
                self._selfroles[ctx.guild.id].remove(role.id)
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.guild.me.color,
                        title="Selfroles Management",
                        description=f"Role {role.mention} has been removed "
                                    f"from selfroles."
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.guild.me.color,
                        title="⚠ Selfroles Management",
                        description=f"Role {role.mention} is not configured as"
                                    f" a selfrole."
                    )
                )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(SelfRoles(bot))