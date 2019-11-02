# -*- coding: utf-8 -*-

"""A reconstruction of my help.py built for the new
discord.py's help.py instead of v1.0.0a's formatter.py

All help messages will be embed and pretty.

Whereas previously, I used formatter.py's code and shimmed
Embeds in, this time, it is simpler to override the methods
help.py exposes for subclassing. It's less stolen code, but
still follows the same logic as the builtin help command

Cog class name becomes Category name.
Docstr on cog class becomes Category description.
Docstr on command definition becomes command summary and usage.
Use [p] in command docstr for bot prefix.

See [p]help here for example.

await bot.formatter.send_help_for(ctx, command, [msg]) to
send help page for command. Optionally pass a string as
third arg to add a more descriptive message to help page.
e.g. send_help_for(ctx, ctx.command, "Missing required arguments")

discord.py v1.2.4

Copyrights to logic of discord help.py belong to Rapptz (Danny)
Everything else credit to SirThane#1780"""


from discord import Colour, DMChannel, Embed
from discord.abc import Messageable
from discord.ext.commands import Cog, Command, Context, Group
from discord.ext.commands.help import HelpCommand as BaseHelpCommand
from typing import Dict, List, Optional, Union

try:
    # My subclassing of Bot
    from cogs.utils.classes import Bot
except ImportError:
    # So I can provide this cog to others
    from discord.ext.commands import Bot


ZWSP = u'\u200b'


class HelpCommand(BaseHelpCommand):
    """The implementation of the help command.

    This implementation formats the help pages into embeds instead of
    markdown command blocks. I like pretty things. Sue me.

    This inherits from :class:discord.ext.commands.help.`HelpCommand`.
    It extends it with the following attributes.

    Attributes
    ------------
    dm_help: Optional[:class:`bool`]
        A tribool that indicates if the help command should DM the user instead of
        sending it to the channel it received it from. If the boolean is set to
        ``True``, then all help output is DM'd. If ``False``, none of the help
        output is DM'd. If ``None``, then the bot will only DM when the help
        message becomes too long (dictated by more than :attr:`dm_help_threshold` characters).
        Defaults to ``False``.
    help: :class:`str`
        The string that will be set as the help command's help manual entry page
    """

    def __init__(self, **options):
        self.dm_help = options.pop('dm_help', False)

        # Used for send_help_for
        # Stored as class attribute instead of passing as parameter so we don't need to override command_callback
        self._title = None

        # Command.short_doc splits Command.help, not raw docstr from inspect, so this sets help_command.short_doc too
        self.help = options.pop("help", "Shows Help Manual Documentation\n\n"
                                        ""
                                        "`[p]help` for all commands\n"
                                        "`[p]help command` for a command's help page\n"
                                        "`[p]help Category` for all commands in a Category")

        super().__init__(command_attrs={"help": self.help}, **options)

    """ ##################################################
        # Special attributes for command/bot information #
        ################################################## """

    @property
    def bot(self) -> Bot:
        return self.ctx.bot

    @property
    def prefix(self) -> str:
        return self.bot.command_prefix

    @property
    def ctx(self) -> Context:
        """Short name for context I use more commonly in signatures"""
        return self.context

    @ctx.setter
    def ctx(self, context: Context):
        self.context = context

    @property
    def is_dm(self) -> bool:
        """Returns True if command or caller is from DMs"""
        return isinstance(self.ctx.channel, DMChannel)

    """ ##############################################
        # Attributes for constructing the base embed #
        ############################################## """

    def em_base(self) -> Embed:
        """Prepare a basic embed that will be common to all outputs"""
        em = Embed(title=self.title, description=ZWSP, color=self.color)
        em.set_author(**self.author)
        em.set_footer(text=self.footer)

        return em

    @property
    def title(self) -> Optional[str]:
        """An optional message that can be sent to send_help_for that adds to Embed title"""
        return self._title

    @title.setter
    def title(self, msg: Optional[str]):
        self._title = msg

    @property
    def author(self) -> Dict[str, str]:
        """Returns an author dict for constructing Embed"""

        # No display names in DMs
        if self.dm_help:
            name = self.bot.user.name
        else:
            name = self.ctx.guild.me.display_name

        author = {
            'name': f'{name} Help Manual',
            'icon_url': self.avatar
        }
        return author

    @property
    def avatar(self) -> str:
        """Returns web URL for bot account's avatar"""
        return self.bot.user.avatar_url_as(format='png')

    @property
    def color(self) -> Colour:
        """Returns current role color of bot if from Guild, or default Embed color if DM"""
        if self.is_dm:
            return Embed.Empty
        else:
            return self.ctx.guild.me.color

    @property
    def footer(self) -> str:
        """Returns help command's ending note"""
        command_name = self.invoked_with if self.invoked_with else "help"
        prefix = self.bot.command_prefix
        return f"Type {prefix}{command_name} command for more info on a command.\n" \
               f"You can also type {prefix}{command_name} Category for more info on a category."

    @property
    def dest(self) -> Messageable:
        """Returns the destination Help output will be sent to"""
        if self.dm_help is True:
            return self.ctx.author
        else:
            return self.ctx

    """ ##################
        # Error handling #
        ################## """

    async def send_error_message(self, error: str):
        """Called in help callback, so we need to override it to use new Embeds"""
        await self.send_help_for(self.ctx, self.ctx.command, error)

    async def send_help_for(self, ctx: Context, cmd: Union[Cog, Command, Group] = None, msg: Optional[str] = None):
        """Can be accessed as a method of bot.help_command to send help pages
        from outside of [p]help. Useful in on_command_error event. Be careful
        as this method is not the builtin default help_command and will be
        removed if the cog is unloaded"""

        # Set the title of the embed so custom messages can be added in
        self.title = msg

        # command kwarg is string
        # Good thing Cog, Command, and Group all have .qualified_name
        # If no cmd, Bot help page will be sent
        await self.command_callback(ctx, command=cmd.qualified_name if cmd else None)

        # Remove title, so it doesn't carry over
        # Would move ot prepare_help_command, but it is called in command_callback
        self.title = None

    async def prepare_help_command(self, ctx: Context, cmd: Optional[str] = None):
        """Method called before command processing"""
        self.ctx = ctx

    """ ###########################################
        # Callbacks for formatting Embeds to send #
        ########################################### """

    async def send_bot_help(self, mapping: Dict[Union[Cog, None], List[Command]], msg: str = None):
        """Prepares help for help command with no argument"""
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

    async def send_command_help(self, cmd: Command):
        """Prepares help when argument is a Command"""
        em = self.em_base()
        em.description = f"`Syntax: {self.get_command_signature(cmd)}`"

        if cmd.help:  # TODO: Hella need to refactor, but working for now.
            if cmd.short_doc == cmd.help:
                doc = cmd.short_doc if cmd.short_doc else cmd.name
            else:
                doc = cmd.help.replace(cmd.short_doc, "").strip("\n").replace("[p]", self.prefix)
        else:
            doc = cmd.short_doc if cmd.short_doc else cmd.name

        field = {
            "name": f"__{cmd.short_doc}__" if cmd.short_doc else f"__{cmd.name}__",
            "value": doc,
            "inline": False
        }
        em.add_field(**field)

        await self.dest.send(embed=em)

    async def send_group_help(self, group: Group):
        """Prepares help when argument is a command Group"""
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
        """Prepares help when argument is a Cog"""

        em = self.em_base()

        # If cog class has a docstring, it's set as description
        # Set as Embed description
        # If no description, set Cog name
        em.description = cog.description.replace("[p]", self.prefix) if cog.description else cog.qualified_name

        # Get list of un-hidden, enabled commands that the invoker passes the checks to run
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
    """Formats and Provides Help Manual Documentation for Commands

    `[p]help` will show all available commands
    `[p]help Category` will show all commands belonging to a category
    `[p]help command` will show a command's help page and all available subcommands if any"""

    def __init__(self, bot: Bot):
        self.bot = bot

        # Store the currently loaded implementation of HelpCommand
        self._original_help_command = bot.help_command

        # Replace currently loaded help_command with ours and set this cog as cog so it's not uncategorized
        bot.help_command = HelpCommand(dm_help=self.bot.dm_help)
        bot.help_command.cog = self

        # Make send_help_for available as a coroutine method of Bot
        bot.send_help_for = bot.help_command.send_help_for

    def cog_unload(self):

        # Use :param cog property setter to remove Cog from help_command
        self.bot.help_command.cog = None

        # Restore the help_command that was loaded before cog load
        self.bot.help_command = self._original_help_command


def setup(bot: Bot):
    bot.add_cog(Help(bot))
