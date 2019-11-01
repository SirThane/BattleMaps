# -*- coding: utf-8 -*-

from discord import Colour, DMChannel, Embed
from discord.abc import Messageable
from discord.ext.commands import Cog, Command, Context, Group
from discord.ext.commands.help import HelpCommand as BaseHelpCommand
from typing import Dict, List, Union

from cogs.utils.classes import Bot
from cogs.utils.utils import ZWSP


class HelpCommand(BaseHelpCommand):
    """The implementation of the default help command.

    This inherits from :class:`HelpCommand`.

    It extends it with the following attributes.

    Attributes
    ------------
    width: :class:`int`
        The maximum number of characters that fit in a line.
        Defaults to 80.
    sort_commands: :class:`bool`
        Whether to sort the commands in the output alphabetically. Defaults to ``True``.
    dm_help: Optional[:class:`bool`]
        A tribool that indicates if the help command should DM the user instead of
        sending it to the channel it received it from. If the boolean is set to
        ``True``, then all help output is DM'd. If ``False``, none of the help
        output is DM'd. If ``None``, then the bot will only DM when the help
        message becomes too long (dictated by more than :attr:`dm_help_threshold` characters).
        Defaults to ``False``.
    commands_heading: :class:`str`
        The command list's heading string used when the help command is invoked with a category name.
        Useful for i18n. Defaults to ``"Commands:"``
    no_category: :class:`str`
        The string used when there is a command which does not belong to any category(cog).
        Useful for i18n. Defaults to ``"No Category"``
    """

    def __init__(self, **options):
        self.dm_help = options.pop('dm_help', False)
        self.help = options.pop("help", "Shows Help Manual Documentation\n\n"
                                        ""
                                        "`[p]help` for all commands\n"
                                        "`[p]help command` for a command's help page\n"
                                        "`[p]help Category` for all commands in a Category")

        super().__init__(command_attrs={"help": self.help}, **options)

    @property
    def is_dm(self) -> bool:
        """Returns True if command or caller is from DMs"""
        return isinstance(self.context.channel, DMChannel)

    @property
    def bot(self):
        return self.context.bot

    @property
    def prefix(self):
        return self.bot.command_prefix

    @property
    def author(self) -> Dict[str, str]:
        """Returns an author dict for constructing Embed"""
        # TODO: Before using display name, need to see how I'll expose send_help_for
        name = self.bot.user.name
        author = {
            'name': f'{name} Help Manual',
            'icon_url': self.avatar
        }
        return author

    @property
    def avatar(self):
        """Returns web URL for bot account's avatar"""
        return self.bot.user.avatar_url_as(format='png')

    @property
    def color(self) -> int:
        """Returns current role color of bot if from Guild, or default Embed color if DM"""
        if self.is_dm:
            return Colour.default().value
        else:
            return self.context.guild.me.color.value

    @property
    def ending_note(self):
        """Returns help command's ending note"""
        command_name = self.invoked_with if self.invoked_with else "help"
        prefix = self.bot.command_prefix
        return f"Type {prefix}{command_name} command for more info on a command.\n" \
               f"You can also type {prefix}{command_name} category for more info on a category."

    @property
    def dest(self) -> Messageable:
        """Returns the destination Help output will be sent to"""
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        else:
            return ctx

    def em_base(self) -> Embed:
        """Prepare a basic embed that will be common to all outputs"""
        em = Embed(description=ZWSP, color=self.color)
        em.set_author(**self.author)
        em.set_footer(text=self.ending_note)

        return em

    async def prepare_help_command(self, ctx: Context, command=None):
        """Method called before command processing"""
        self.context = ctx

    async def send_bot_help(self, mapping: Dict[Union[Cog, None], List[Command]]):
        em = self.em_base()
        no_category = f"{ZWSP}No Category:"

        if self.bot.description:
            em.description = f"*{self.bot.description}*"
        else:
            em.description = f" {ZWSP}"

        for cog, cmds in mapping.items():
            cmds = await self.filter_commands(cmds, sort=True)
            if not cmds:
                continue
            field = {
                "name": f"**__{cog.qualified_name if cog else '{}'.format(no_category)}__**",
                "value": "\n".join([f"**{self.prefix}{cmd.name}:**   {cmd.short_doc}" for cmd in cmds]),
                "inline": False
            }
            em.add_field(**field)

        await self.dest.send(embed=em)  # TODO: Refactor into self.send() for pagination

    async def send_command_help(self, command: Command):
        em = self.em_base()
        em.description = f"`Syntax: {self.get_command_signature(command)}`"

        if command.help:  # TODO: Hella need to refactor, but working for now.
            if command.short_doc == command.help:
                doc = command.short_doc if command.short_doc else command.name
            else:
                doc = command.help.replace(command.short_doc, "").strip("\n").replace("[p]", self.prefix)
        else:
            doc = command.short_doc if command.short_doc else command.name

        field = {
            "name": f"__{command.short_doc}__" if command.short_doc else f"__{command.name}__",
            "value": doc,
            "inline": False
        }
        em.add_field(**field)

        await self.dest.send(embed=em)

    async def send_group_help(self, group: Group):
        em = self.em_base()
        em.description = f"`Syntax: {self.get_command_signature(group)}`".replace("[p]", self.prefix)

        if group.help:
            if group.short_doc == group.help:
                doc = group.short_doc if group.short_doc else group.name
            else:
                doc = group.help.replace(group.short_doc, "").strip("\n").replace("[p]", self.prefix)
        else:
            doc = group.short_doc if group.short_doc else group.name

        field = {
            "name": f"__{group.short_doc}__" if group.short_doc else f"__{group.name}__",
            "value": doc,
            "inline": False
        }
        em.add_field(**field)

        cmds = await self.filter_commands(group.commands, sort=True)
        if cmds:
            field = {
                "name": "**__Subcommands:__**",
                "value": "\n".join([f"**{cmd.name}:**   {cmd.short_doc}" for cmd in group.commands]),
                "inline": False
            }
            em.add_field(**field)

        await self.dest.send(embed=em)

    async def send_cog_help(self, cog: Cog):
        em = self.em_base()

        if cog.description:
            em.description = cog.description.replace("[p]", self.prefix)
        else:
            em.description = cog.qualified_name

        cmds = await self.filter_commands(cog.get_commands(), sort=True)
        if cmds:
            field = {
                "name": "**__Commands:__**",
                "value": "\n".join([f"**{self.prefix}{cmd.name}**   {cmd.short_doc}" for cmd in cmds]),
                "inline": False
            }
            em.add_field(**field)

        await self.dest.send(embed=em)


class Help(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand(dm_help=self.bot.dm_help)
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command.cog = None
        self.bot.help_command = self._original_help_command


def setup(bot: Bot):
    bot.add_cog(Help(bot))
