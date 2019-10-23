"""Cog containing all global bot events"""

import traceback
import sys
import discord
from discord.ext import commands
from cogs.utils import errors

# TODO: Create events cog


WELCOME = "Welcome to AWBW Discord Server {}! Present yourself and have fun!"
LEAVE = "{} has left our army... Be happy in peace."


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.awbw = bot.get_guild(184502171117551617)       # Not Skype
        self.awbw = bot.get_guild(313453805150928906)       # AWBW Guild
        # self.channel = bot.get_channel(315232431835709441)  # Circlejerk Py
        self.channel = bot.get_channel(313453805150928906)  # AWBW General
        if self.awbw:
            self.sad_andy = discord.utils.get(  # :sad_andy: emoji
                self.awbw.emojis, id=325608374526017536
            )

    async def on_member_join(self, member: discord.Member) -> None:
        if member.guild.id != self.awbw.id:
            return
        await self.channel.send(WELCOME.format(member.mention))

    async def on_member_remove(self, member: discord.Member) -> None:
        if member.guild.id != self.awbw.id:
            return
        await self.channel.send(LEAVE.format(member.display_name))

    async def on_member_ban(self, member: discord.Member) -> None:
        pass
        # await self.channel.send(f"{member.display_name} test. (ban)")

    async def on_member_unban(self, member: discord.Member) -> None:
        pass
        # await self.channel.send(f"{member.display_name} test. (unban)")

    # async def on_message(self, message: discord.Message) -> None:
    #     if "airport" in message.content.lower():
    #         await message.add_reaction(self.sad_andy)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                content='This command cannot be used in private messages.'
            )

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                content='This command is disabled and cannot be used.'
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await self.bot.formatter.format_help_for(
                ctx, ctx.command, "You are missing required arguments."
            )

        elif isinstance(error, commands.CommandNotFound):
            await self.bot.formatter.format_help_for(
                ctx, self.bot.get_command("help"), "Command not found."
            )

        elif isinstance(error, commands.CheckFailure):
            em = discord.Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="Get your hands off that! \n"
                            "What'd'ya say you take a look and try it again.\n"
                            "\n```\nThe map you uploaded contained\n"
                            "rows with a differing amounts of\n"
                            "columns. Check your map and try again.\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, errors.AWBWDimensionsError):
            em = discord.Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="I can't take that map. The edges are all wrong.\n"
                            "What'd'ya say you take a look and try it again.\n"
                            "\n```\nThe map you uploaded contained\n"
                            "rows with a differing amounts of\n"
                            "columns. Check your map and try again.\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, errors.InvalidMapError):
            em = discord.Embed(
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

        elif isinstance(error, errors.NoLoadedMapError):
            em = discord.Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="You can try that that all you like, but you\n"
                            "ain't doin' nothin' without a map to do it on.\n"
                            "\n```\nThis command requires you load a map first"
                            ".\nMake sure you load a map with `$$map load`\n"
                            "first. If you are having trouble, try looking\n"
                            "in `$$help`\n```")
            await ctx.send(embed=em)

        elif isinstance(error, errors.UnimplementedError):
            em = discord.Embed(
                color=ctx.guild.me.color,
                title="⚠  Woah there, buddy!",
                description="I ain't got the stuff to do that quite yet.\n"
                            "Hold yer horses. I'll have it ready here soon.\n"
                            "\n```\nThis feature has not yet been implemented."
                            "\n```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, commands.CommandInvokeError):
            print(
                'In {0.command.qualified_name}:'.format(ctx),
                file=sys.stderr
            )
            print(
                '{0.__class__.__name__}: {0}'.format(error.original),
                file=sys.stderr
            )
            traceback.print_tb(
                error.__traceback__,
                file=sys.stderr
            )

        else:
            traceback.print_tb(
                error.__traceback__,
                file=sys.stderr
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Events(bot))
