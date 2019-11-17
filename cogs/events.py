"""Cog containing all global bot events"""


from datetime import datetime
from discord import Embed, Member, Message
from discord.utils import get
from discord.ext.commands import Cog, Context
from discord.ext.commands.errors import (
    CheckFailure,
    CommandInvokeError,
    CommandNotFound,
    DisabledCommand,
    MissingRequiredArgument,
    NoPrivateMessage
)
from pytz import timezone
from typing import Union

from utils.classes import Bot
from utils.errors import *


WELCOME = "**Welcome to AWBW Discord Server {}!**\nPresent yourself and have fun!"
LEAVE = "**{} has left our army...**\nBe happy in peace."


tz = timezone('America/Kentucky/Louisville')


class Events(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = bot.db
        self.config = f"{bot.APP_NAME}:events"

        self.errorlog = bot.errorlog

        # self.awbw = bot.get_guild(184502171117551617)               # Not Skype
        self.awbw = bot.get_guild(313453805150928906)               # AWBW Guild
        # self.channel = bot.get_channel(315232431835709441)          # Circlejerk Py
        self.channel = bot.get_channel(313453805150928906)          # AWBW General
        self.notifchannel = bot.get_channel(637877898560143363)     # BattleMaps-Notifs

        if self.awbw:
            self.sad_andy = get(self.awbw.emojis, id=325608374526017536)  # :sad_andy: emoji

    @Cog.listener(name="on_member_join")
    async def on_member_join(self, member: Member):
        if not self.awbw:
            return
        if member.guild.id != self.awbw.id:
            return
        em = Embed(
            description=WELCOME.format(member.mention),
            color=member.guild.me.colour
        )
        await self.channel.send(embed=em)

    @Cog.listener(name="on_member_remove")
    async def on_member_remove(self, member: Member):
        if not self.awbw:
            return
        if member.guild.id != self.awbw.id:
            return
        em = Embed(
            description=LEAVE.format(member.display_name),
            color=member.guild.me.colour
        )
        await self.channel.send(embed=em)

    # @Cog.listener(name="on_message")
    # async def on_message(self, message: discord.Message) -> None:
    #     if "airport" in message.content.lower():
    #         await message.add_reaction(self.sad_andy)

    @Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: Context, error: Union[Exception, CommandError]):
        if isinstance(error, NoPrivateMessage):
            em = Embed(
                color=Embed.Empty,
                title="⚠  Woah there, buddy!",
                description="I ain't even on the clock. \n"
                            "Check that out when I'm in the shop.\n"
                            "\n"
                            "```\n"
                            "This command cannot be used in private messages.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, DisabledCommand):
            em = Embed(
                color=ctx.guild.me.colour,
                title="⚠  Woah there, buddy!",
                description="That there ain't for sale! \n"
                            "Hell, pro'lly don't even work.\n"
                            "Check out som'thin' else.\n"
                            "\n"
                            "```\n"
                            "This command is disabled and cannot be used.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, MissingRequiredArgument):
            await self.bot.help_command.send_help_for(ctx, ctx.command, "You are missing required arguments.")

        elif isinstance(error, CommandNotFound):
            cmd = ctx.command
            await self.bot.help_command.send_help_for(ctx, self.bot.get_command("help"), f"Command `{cmd}` not found.")

        elif isinstance(error, CheckFailure):
            em = Embed(
                color=ctx.guild.me.colour,
                title="⚠  Woah there, buddy!",
                description="Get your hands off that! \n"
                            "That there's for shop staff only.\n"
                            "\n"
                            "```\n"
                            "You do not have the appropriate access for that command.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, AWBWDimensionsError):
            em = Embed(
                color=ctx.guild.me.colour,
                title="⚠  Woah there, buddy!",
                description="I can't take that map. The edges are all wrong.\n"
                            "What'd'ya say you take a look and try it again.\n"
                            "\n"
                            "```\n"
                            "The map you uploaded contained\n"
                            "rows with a differing amounts of\n"
                            "columns. Check your map and try again.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, InvalidMapError):
            em = Embed(
                color=ctx.guild.me.colour,
                title="⚠  Woah there, buddy!",
                description="What are you trying to sell here? Is that even\n"
                            "a map? It don't look like none I ever seen.\n"
                            "\n"
                            "```\n"
                            "The converter was unable to detect a valid\n"
                            "map in your message. Please check your\n"
                            "file and command parameters. If you have\n"
                            "trouble, try in `$$help`\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, NoLoadedMapError):
            em = Embed(
                color=ctx.guild.me.colour,
                title="⚠  Woah there, buddy!",
                description="You can try that that all you like, but you\n"
                            "ain't doin' nothin' without a map to do it on.\n"
                            "\n"
                            "```\n"
                            "This command requires you load a map first.\n"
                            "Make sure you load a map with `$$map load`\n"
                            "first. If you are having trouble, try looking\n"
                            "in `$$help`\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, UnimplementedError):
            em = Embed(
                color=ctx.guild.me.colour,
                title="⚠  Woah there, buddy!",
                description="I ain't got the stuff to do that quite yet.\n"
                            "Hold yer horses. I'll have it ready here soon.\n"
                            "\n"
                            "```\n"
                            "This feature has not yet been implemented.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, CommandInvokeError):
            await self.errorlog.send(error.original, ctx)

        else:
            await self.errorlog.send(error)

    @Cog.listener("on_message")
    async def on_message(self, msg: Message):
        if str(self.bot.user.id) in msg.content:
            ts = tz.localize(datetime.now()).strftime("%b. %d, %Y %I:%M %p")
            author = msg.author
            display_name = f' ({author.display_name})' if author.display_name != author.name else ''
            em = Embed(
                title=f"{msg.guild}: #{msg.channel} at {ts}",
                description=msg.content,
                color=author.colour
            )
            em.set_author(
                name=f"{author.name}#{author.discriminator}{display_name}",
                icon_url=author.avatar_url_as(format="png")
            )
            await self.notifchannel.send(msg.jump_url, embed=em)


def setup(bot: Bot):
    bot.add_cog(Events(bot))
