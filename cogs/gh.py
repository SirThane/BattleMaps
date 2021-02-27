"""Name, credits, license, and general overview of file"""

# Lib
from functools import wraps
from typing import Optional

# Site
from discord.colour import Colour
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import check, command, group
from github.MainClass import Github
from github.GithubException import BadCredentialsException

# Local
from utils.classes import Bot, Embed, SubRedis


class Emoji:
    repo = b"\xF0\x9F\x93\x92".decode("utf8")  # 📒  :ledger:
    gist = b"\xF0\x9F\x93\x84".decode("utf8")  # 📄  :page_facing_up:
    star = b"\xE2\xAD\x90".decode("utf8")      # ⭐  :star:


def is_authed(func):

    @wraps(func)
    async def wrapper(self, ctx: Context, *args, **kwargs):

        if self.gh_client:
            await func(self, ctx, *args, **kwargs)

        else:
            await self.bot.send_help_for(
                ctx, self.bot.get_command("gh auth"),
                "GitHub Application Token missing or invalid.\n"
                "Replace token in database and try re-authenticating."
            )

    return wrapper


class GitHub(Cog):
    """GitHub"""

    def __init__(self, bot: Bot):

        self.bot = bot
        self.config = SubRedis(bot.db, "github")

        self.errorlog = bot.errorlog

        self.gh_client = self.try_auth()

        if self.gh_client:
            self._user = self.user = self.gh_client.get_user()
            self._repo = self.repo = self.user.get_repo(self.bot.APP_NAME)

    def cog_check(self, ctx: Context) -> bool:
        return ctx.

    def try_auth(self) -> Optional[Github]:
        """Create Github client object and attempt hitting API with token"""

        token = self.config.get("token")

        if token:
            try:
                gh_client = Github(token)
                _ = gh_client.get_rate_limit()
                return gh_client

            except BadCredentialsException:
                return None

    @group(name="gh", invoke_without_command=True)
    @is_authed
    async def gh(self, ctx: Context):
        """GitHub

        Something"""
        user = f"[{self.user.name}]({self.user.html_url})" if self.user else "None Selected"
        repo = f"[{self.repo.name}]({self.repo.html_url})" if self.repo else "None Selected"

        em = Embed(
            title="GitHub",
            description=f"**__Current Selections:__**\n"
                        f"__User:__ {user}\n"
                        f"__Repository:__ {repo}",
            color=Colour.green()
        )

        await ctx.send(embed=em)

    @gh.command(name="auth")
    async def auth(self, ctx: Context):
        """Authenticate With GitHub Token

        Something something"""
        pass

    @gh.command(name="user")
    async def user(self, ctx: Context, *, user: str = None):
        """User

        Selects a GitHub user account and shows a brief of the profile.
        `[p]gh user <username>` will select a user account
        `[p]gh user self` will select your user account
        `[p]gh user` will display the currently selected user"""

        try:
            if user == "self":
                self.user = user = self.gh_client.get_user()
            elif user:
                self.user = user = self.gh_client.get_user(user)
            else:
                if self.user:
                    user = self.user
                else:
                    return await self.bot.send_help_for(
                        ctx.command,
                        "No account is currently selected."
                    )

            if self.repo.owner.name != self.user.name:
                self.repo = None

            repos = len(list(user.get_repos()))
            gists = len(list(user.get_gists()))
            stars = len(list(user.get_gists()))

            em = Embed(
                title=f"{user.login}'s Public GitHub Profile",
                description=f"*\"{user.bio}\"*\n\n"
                            f"{Emoji.repo} [Repositories]({user.html_url}?tab=repositories): {repos}\n"
                            f"{Emoji.gist} [Gists](https://gist.github.com/{user.login}): {gists}\n"
                            f"{Emoji.star} [Starred Repositories]({user.html_url}?tab=stars): {stars}",
                color=Colour.green()
            )
            em.set_author(name=user.name, url=user.html_url, icon_url=user.avatar_url)

        except:
            em = Embed(
                title="GitHub: Error",
                description="Unable to load user or user not found",
                color=Colour.red()
            )

        await ctx.send(embed=em)

    @gh.command(name="repo")
    async def repo(self, ctx: Context, *, name: str = None):
        pass

    @gh.group(name="issues", invoke_without_command=True, aliases=["issue"])
    async def issues(self, ctx: Context, state: str = "all"):
        """Issues

        View and manage issues on a repo"""

        state = state.lower()
        if state not in ("open", "closed", "all"):
            return await self.bot.send_help_for(ctx.command, "Valid states: `open`, `closed`, `all`")

        em = Embed()

        for issue in self.repo.get_issues(state=state):
            pass


def setup(bot: Bot):
    """CogName"""
    bot.add_cog(GitHub(bot))
