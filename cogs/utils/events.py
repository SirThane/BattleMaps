"""Cog containing all global bot events"""

from sys import stderr
from traceback import print_tb

from discord import Embed, Member
from discord.utils import get
from discord.ext.commands import CheckFailure, Cog, CommandInvokeError, CommandNotFound, Context, DisabledCommand, MissingRequiredArgument, NoPrivateMessage

from classes.bot import Bot
from cogs.utils.errors import *


WELCOME = "Welcome to AWBW Discord Server {}! Present yourself and have fun!"
LEAVE = "{} has left our army... Be happy in peace."


class Events(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = bot.db
        self.config = f"{bot.APP_NAME}:events"

        # self.awbw = bot.get_guild(184502171117551617)       # Not Skype
        self.awbw = bot.get_guild(313453805150928906)       # AWBW Guild
        # self.channel = bot.get_channel(315232431835709441)  # Circlejerk Py
        self.channel = bot.get_channel(313453805150928906)  # AWBW General

        if self.awbw:
            self.sad_andy = get(self.awbw.emojis, id=325608374526017536)  # :sad_andy: emoji

    @Cog.listener(name="on_member_join")
    async def on_member_join(self, member: Member):
        if member.guild.id != self.awbw.id:
            return
        await self.channel.send(WELCOME.format(member.mention))

    @Cog.listener(name="on_member_remove")
    async def on_member_remove(self, member: Member):
        if member.guild.id != self.awbw.id:
            return
        await self.channel.send(LEAVE.format(member.display_name))

    @Cog.listener(name="on_member_ban")
    async def on_member_ban(self, member: Member):
        pass

    @Cog.listener(name="on_member_unban")
    async def on_member_unban(self, member: Member):
        pass

    # async def on_message(self, message: discord.Message) -> None:
    #     if "airport" in message.content.lower():
    #         await message.add_reaction(self.sad_andy)

    @Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: Context, error):
        if isinstance(error, NoPrivateMessage):
            await ctx.send(
                content='This command cannot be used in private messages.'
            )

        elif isinstance(error, DisabledCommand):
            await ctx.send(
                content='This command is disabled and cannot be used.'
            )

        elif isinstance(error, MissingRequiredArgument):
            pass
            # await self.bot.formatter.format_help_for(
            #     ctx, ctx.command, "You are missing required arguments."
            # )

        elif isinstance(error, CommandNotFound):
            pass
            # await self.bot.formatter.format_help_for(
            #     ctx, self.bot.get_command("help"), "Command not found."
            # )

        elif isinstance(error, CheckFailure):
            em = Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="Get your hands off that! \n"
                            "What'd'ya say you take a look and try it again.\n"
                            "\n```\nThe map you uploaded contained\n"
                            "rows with a differing amounts of\n"
                            "columns. Check your map and try again.\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, AWBWDimensionsError):
            em = Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="I can't take that map. The edges are all wrong.\n"
                            "What'd'ya say you take a look and try it again.\n"
                            "\n```\nThe map you uploaded contained\n"
                            "rows with a differing amounts of\n"
                            "columns. Check your map and try again.\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, InvalidMapError):
            em = Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="What are you trying to sell here? Is that even\n"
                            "a map? It don't look like none I ever seen.\n\n"
                            "```\nThe converter was unable to detect a valid\n"
                            "map in your message. Please check your\n"
                            "file and command parameters. If you have\n"
                            "trouble, try in `$$help`\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, NoLoadedMapError):
            em = Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="You can try that that all you like, but you\n"
                            "ain't doin' nothin' without a map to do it on.\n"
                            "\n```\nThis command requires you load a map first"
                            ".\nMake sure you load a map with `$$map load`\n"
                            "first. If you are having trouble, try looking\n"
                            "in `$$help`\n```")
            await ctx.send(embed=em)

        elif isinstance(error, UnimplementedError):
            em = Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="I ain't got the stuff to do that quite yet.\n"
                            "Hold yer horses. I'll have it ready here soon.\n"
                            "\n```\nThis feature has not yet been implemented."
                            "\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, CommandInvokeError):  # TODO: Make this send to a debug channel instead
            print('In {0.command.qualified_name}:'.format(ctx), file=stderr)
            print('{0.__class__.__name__}: {0}'.format(error.original), file=stderr)
            print_tb(error.__traceback__, file=stderr)

        else:
            print_tb(error.__traceback__, file=stderr)


def setup(bot: Bot):
    bot.add_cog(Events(bot))
