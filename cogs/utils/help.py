# -*- coding: utf-8 -*-

"""
A reconstruction of my help.py built for the new
discord.py's help.py instead of v1.0.0a-'s formatter.py

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
Everything else credit to SirThane#1780
"""


from discord import Colour, DMChannel, Embed, Member, Reaction, User
from discord.abc import Messageable
from discord.ext.commands import Cog, Command, Context, Group
from discord.ext.commands.help import HelpCommand as BaseHelpCommand
from typing import Dict, List, Optional, Tuple, Union

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

        # Number of fields before a help command's output gets paginated
        self._field_limit = options.pop("field_limit", 7)

        # Command.short_doc splits Command.help, not raw docstr from inspect, so this sets help_command.short_doc too
        self.help = options.pop("help", "Shows Help Manual Documentation\n\n"
                                        ""
                                        "`[p]help` for all commands\n"
                                        "`[p]help command` for a command's help page\n"
                                        "`[p]help Category` for all commands in a Category")

        super().__init__(command_attrs={"help": self.help}, **options)

    """ ################################################
         Special attributes for command/bot information
        ################################################ """

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

    """ ############################################
         Attributes for constructing the base embed
        ############################################ """

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

    """ ############
         Pagination
        ############ """

    async def send(self, em: Embed, fields: List[Dict[str, Union[str, bool]]]):
        for field in fields:
            em.add_field(**field)
        await self.dest.send(embed=em)

    """ ################
         Error handling
        ################ """

    async def send_error_message(self, error: str):
        """Called in help callback, so we need to override it to use new Embeds"""
        await self.send_help_for(self.ctx, self.ctx.command, error)

    """ ########################
         Formatting and sending
        ######################## """

    async def prepare_help_command(self, ctx: Context, cmd: Optional[str] = None):
        """Method called before command processing"""
        self.ctx = ctx

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

    def format_doc(self, item: Union[Bot, Cog, Command, Group]) -> Tuple[str, str]:
        if isinstance(item, Bot):
            if item.description:
                desc = item.description.replace("[p]", self.prefix)

                # Maximum embed body description length
                if len(desc) > 2043:
                    desc = f"{desc[:2043]}..."

                return f"*{desc}*", ""
            else:
                return f"*{item.user.name}*", ""

        elif isinstance(item, Cog):
            if item.description:
                # "CogName", "*Description: $command for use*"
                return item.qualified_name, f"*{item.description.replace('[p]', self.prefix)}*"
            else:
                # "CogName", "*CogName*"
                return item.qualified_name, f"*{item.qualified_name}*"

        elif isinstance(item, Command) or isinstance(item, Group):
            brief = item.brief if item.brief else item.short_doc
            desc = item.help

            # .help will be None if no docstr
            if desc:
                desc = desc.replace(brief, "").strip("\n").replace("[p]", self.prefix)

            # If no .help or if .help same as .short_doc
            if not desc:
                desc = "No help manual page exists for this command."

            # If no .brief or no .short_doc, change to .name after checking .help in case name is mentioned in .help
            if not brief:
                brief = item.name

            return brief, desc

        else:
            raise TypeError(f"{str(item)}: {item.__class__.__name__} not a subclass of Bot, Cog, Command, or Group.")

    def format_cmds_list(self, cmds: List[Union[Command, Group]]) -> str:
        """Formats and paginates the list of a cog's commands
        Maximum Embed field value is 1024"""

        lines = list()

        for cmd in cmds:

            # Get and format the one line entry for cmd
            brief, _ = self.format_doc(cmd)
            lines.append(f"**{self.prefix}{cmd.qualified_name}{ZWSP}**   {brief}")

        return "\n".join(lines)

    @staticmethod
    def paginate_field(
            name: str,
            value: str,
            wrap: str = "{}{}",
            cont: str = " (Cont.)"
    ) -> List[Dict[str, Union[str, bool]]]:
        """Takes parameters for an Embed field and returns a
        list of field dicts with values under 1024 characters

        :param name:
            :class:`str` that will be used as field header
        :param value:
            :class:`str` that will be paginated for field values
        :param wrap:
            :class:`str` that will be formatted for field headers
            Must be a string that will accept .format() with two
            parameters. ``name`` will be inserted first, then ``cont``
        :param cont:
            :class:`str` that will extend header

        e.g. name="Test", wrap="__{}{}__", cont=" (Continued)"
             Header 1: "__Test__"
             Header 2: "__Test (Continued)__"
        """

        fields = list()

        # Account for large cogs and split them into separate fields
        field = {
            "name": wrap.format(name, ""),
            "value": "",
            "inline": False
        }

        values = value.split("\n")

        for value in values:

            # Embed field value maximum length, less 1 for line return
            if len(value) + len(field["value"]) < 1023:
                field["value"] += f"\n{value}"
            else:

                # Add field to fields list and start a new one
                fields.append(field)
                field = {
                    "name": f"**__{name}{cont}:__**",
                    "value": value,
                    "inline": False
                }

        else:
            # Add the field if one field or add the last field if multiple
            fields.append(field)

        return fields

    """ #####################################################################################
         Callbacks for help command for arguments Bot [no argument], Cog, Command, and Group
        ##################################################################################### """

    async def send_bot_help(self, mapping: Dict[Union[Cog, None], List[Command]], msg: str = None):
        """Prepares help for help command with no argument"""

        em = self.em_base()
        fields = list()

        # Set Embed body description as cog's docstr
        em.description, _ = self.format_doc(self.bot)

        for cog, cmds in mapping.items():

            # Get list of unhidden, commands in cog that user passes checks for
            cmds = await self.filter_commands(cmds, sort=True)

            # If cog doesn't have any commands user can run, skip it
            if not cmds:
                continue

            # Get header (Category name) for Embed field
            category = cog.qualified_name if cog else "No Category"

            # Add fields for commands list
            fields.extend(self.paginate_field(category, self.format_cmds_list(cmds), "**__{}{}__**"))

        await self.send(em, fields)

    async def send_cog_help(self, cog: Cog):
        """Prepares help when argument is a Cog"""

        em = self.em_base()
        fields = list()

        # If cog class has a docstring, it's set as description
        # If no description, set Cog name
        em.description = "**__{}__**\n{}".format(*self.format_doc(cog))

        # Get list of un-hidden, enabled commands that the invoker passes the checks to run
        cmds = await self.filter_commands(cog.get_commands(), sort=True)

        # Add fields for commands list
        if cmds:
            fields.extend(self.paginate_field("Commands", self.format_cmds_list(cmds), "**__{}{}__**"))

        await self.send(em, fields)

    async def send_command_help(self, cmd: Command):
        """Prepares help when argument is a Command"""

        em = self.em_base()
        fields = list()

        # Get command usage
        if cmd.usage:
            usage = f"`Syntax: {self.prefix}{cmd.qualified_name} {cmd.usage}`"
        else:
            usage = f"`Syntax: {self.get_command_signature(cmd)}`"

        # Add command name and usage to Embed body description
        em.description = f"**__{cmd.qualified_name}__**\n{usage}"

        # Add fields for command help manual
        fields.extend(self.paginate_field(*self.format_doc(cmd), "__{}{}__"))

        await self.send(em, fields)

    async def send_group_help(self, group: Group):
        """Prepares help when argument is a command Group"""

        em = self.em_base()
        fields = list()

        # Get command usage
        if group.usage:
            usage = f"`Syntax: {self.prefix}{group.qualified_name} {group.usage}`"
        else:
            usage = f"`Syntax: {self.get_command_signature(group)}`"

        # Add command name and usage to Embed body description
        em.description = f"**__{group.qualified_name}__**\n{usage}"

        # Add fields for command help manual
        fields.extend(self.paginate_field(*self.format_doc(group), "__{}{}__"))

        cmds = await self.filter_commands(group.commands, sort=True)
        if cmds:
            fields.extend(self.paginate_field("Subcommands", self.format_cmds_list(cmds), "**__{}{}__**"))

        await self.send(em, fields)


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

    @Cog.listener("on_reaction_add")
    async def _on_reaction_add(self, react: Reaction, user: Union[Member, User]):
        pass


def setup(bot: Bot):
    bot.add_cog(Help(bot))
