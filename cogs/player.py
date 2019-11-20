
# Lib
from datetime import timedelta

# Site
from discord.channel import TextChannel, VoiceChannel
from discord.colour import Colour
from discord.embeds import Embed
from discord.ext.commands import check, command, group
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError
from discord.guild import Guild
from discord.member import Member, VoiceState
from typing import Optional

# Local
from utils.checks import sudo
from utils.classes import Bot
from utils.utils import SubRedis
from utils.session import Session
from utils.track import MP3Track, YouTubeTrack


async def session_is_running(ctx: Context) -> bool:
    """A player is not running on this server."""
    return ctx.cog.get_session(ctx.guild) is not None


async def user_is_in_voice_channel(ctx: Context) -> bool:
    """You are currently not in a voice channel."""
    return isinstance(ctx.author, Member) and ctx.author.voice is not None


async def user_is_listening(ctx: Context) -> bool:
    """You are currently not listening to the bot."""
    session = ctx.cog.get_session(ctx.guild)
    return session is not None and ctx.author in session.listeners


async def user_has_required_permissions(ctx: Context) -> bool:
    """You do not have the required role to perform this action."""
    session = ctx.cog.get_session(ctx.guild)
    return session is None or session.user_has_permission(ctx.author)


class Player(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.root_db = bot.db

        self.config = SubRedis(bot.db, f"{bot.APP_NAME}:player")
        self.config_bot = SubRedis(bot.db, f"{bot.APP_NAME}:config")

        self.sessions = dict()

        self.bot.loop.create_task(self._init_all_sessions())

    """ ##############################################
         Setup, Session Initialization, And Breakdown
        ############################################## """

    def get_session(self, guild: Guild) -> Optional[Session]:
        return self.sessions.get(guild)

    async def init_session(
            self,
            guild: Guild,
            voice: VoiceChannel,
            log: TextChannel = None,
            run_forever: bool = True,
            **session_config
    ):
        session = Session(
            self.bot,
            self.config,
            self,
            voice,
            log=log,
            run_forever=run_forever,
            **session_config
        )

        # Add session to sessions and start voice
        self.sessions[guild] = session
        await session.session_task()

        # When voice has ended, disconnect and remove session
        await session.voice.disconnect()
        self.sessions.pop(guild)

    async def _init_all_sessions(self):
        """Read configs from db and init all sessions"""

        # Cannot start sessions before bot is logged in and ready
        await self.bot.wait_until_ready()

        for init_session_config in self.config.scan_iter("sessions*"):
            session_config = self.config.hgetall(init_session_config)

            guild = self.bot.get_guild(int(session_config.pop("guild_id")))
            voice = self.bot.get_channel(int(session_config.pop("voice")))

            l_id = session_config.pop("log", None)
            if l_id:
                log = self.bot.get_channel(int(l_id))
            else:
                log = None

            self.bot.loop.create_task(self.init_session(guild, voice, log=log, run_forever=True, **session_config))

    def cog_unload(self):
        """Stop voice on all sessions to cleanly leave session loop and disconnect voice"""
        for session in self.sessions.values():
            session.stop()

    """ ##################
         Requesting Songs
        ################## """

    @group(name="request", aliases=["play"], invoke_without_command=True, enabled=False)
    @check(user_is_in_voice_channel)
    @check(user_has_required_permissions)
    async def request(self, ctx: Context, *, request):
        """Adds a YouTube video to the requests queue.

        request: YouTube search query.
        """

        session = self.get_session(ctx.guild)

        if session is None:
            session = self.sessions[ctx.guild] = Session(
                self.bot,
                self.config,
                self,
                ctx.author.voice.channel
            )

        await ctx.send(**request.request_message)
        session.queue.add_request(request)

    @request.command(name="mp3", enabled=False)
    async def request_mp3(self, ctx: Context, *, request: MP3Track):
        """Adds a local MP3 file to the requests queue.

        request: Local track search query.
        """
        await ctx.invoke(self.request, request=request)

    @request.command(name="youtube", enabled=False)
    async def request_youtube(self, ctx: Context, *, request: YouTubeTrack):
        """Adds a YouTube video to the requests queue.

        request: YouTube search query.
        """
        await ctx.invoke(self.request, request=request)

    """ ################
         Queue Commands
        ################ """

    @command(name="skip")
    @check(session_is_running)
    @check(user_is_listening)
    async def skip(self, ctx: Context):
        """Skips the currently playing track."""

        session = self.get_session(ctx.guild)

        if ctx.author in session.skip_requests:
            raise CommandError("You have already requested to skip.")

        session.skip_requests.append(ctx.author)
        skips_needed = len(list(session.listeners)) // 2 + 1

        if len(session.skip_requests) >= skips_needed:
            session.voice.stop()

        else:
            em = Embed(
                colour=Colour.dark_green(),
                title="Skip video",
                description=f"You currently need "
                            f"**{skips_needed - len(session.skip_requests)}** "
                            f"more votes to skip this track."
            )

            await ctx.send(embed=em)

    @command(name='repeat')
    @check(session_is_running)
    @check(user_is_listening)
    async def repeat(self, ctx: Context):
        """Repeats the currently playing track."""

        session = self.get_session(ctx.guild)

        if ctx.author in session.repeat_requests:
            raise CommandError('You have already requested to repeat.')

        session.repeat_requests.append(ctx.author)
        repeats_needed = len(list(session.listeners)) // 2 + 1

        if len(session.repeat_requests) >= repeats_needed:
            session.queue.add_request(session.current_track, at_start=True)

        else:
            em = Embed(
                colour=Colour.dark_green(),
                title='Repeat track',
                description=f'You currently need '
                            f'**{repeats_needed - len(session.repeat_requests)}** '
                            f'more votes to repeat this track.'
            )

            await ctx.send(embed=em)

    @command(name='playing', aliases=['now'])
    @check(session_is_running)
    async def playing(self, ctx: Context):
        """Retrieves information on the currently playing track."""

        session = self.get_session(ctx.guild)

        play_time = session.current_track.play_time
        track_length = session.current_track.length

        play_time_str = str(timedelta(seconds=play_time))
        length_str = str(timedelta(seconds=track_length))

        seek_length = 50
        seek_distance = round(seek_length * play_time / track_length)

        message = session.current_track.playing_message
        message['embed'].add_field(
            name=f'{play_time_str} / {length_str}',
            value=f'`{"-" * seek_distance}|{"-" * (seek_length - seek_distance)}`',
            inline=False
        )

        await ctx.send(**message)

    @command(name="queue", aliases=["upcoming"], enabled=False)
    @check(session_is_running)
    async def queue(self, ctx: Context):

        session = self.get_session(ctx.guild)

        em = Embed(
            colour=Colour.dark_green(),
            title="Upcoming requests"
        )

        for index, track in enumerate(session.queue.requests[:10], 1):
            em.add_field(
                name=f"{index} - Requested by {track.requester}",
                value=track.information
            )

        if not em.fields:
            em.description = "There are currently no requests"

        await ctx.send(embed=em)

    """ ################
         Admin Commands
        ################ """

    @sudo()
    @command(name="stop")
    async def stop(self, ctx: Context):
        session = self.get_session(ctx.guild)
        if session:
            session.stop()

    """ ########
         Events
        ######## """

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, _: VoiceState, after: VoiceState):

        session = self.get_session(member.guild)

        if session is not None:
            if after is None and member in session.skip_requests:
                session.skip_requests.remove(member)

            if session.voice is not None:
                session.check_listeners()

    # async def cog_command_error(self, ctx: Context, error: Union[Exception, CommandError]):


def setup(bot: Bot):
    """Player"""
    bot.add_cog(Player(bot))
