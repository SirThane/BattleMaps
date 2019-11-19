
from asyncio import Event
from asyncio.tasks import create_task
# from discord.activity import Activity
from discord.channel import TextChannel, VoiceChannel
from discord.client import Client
# from discord.enums import ActivityType
from discord.ext.commands.cog import Cog
from discord.member import Member
from typing import Generator

from utils.queue import Queue, Radio
from utils.utils import SubRedis


class Session:

    def __init__(
            self,
            bot: Client,
            config: SubRedis,
            cog: Cog,
            voice_channel: VoiceChannel,
            *,
            log_channel: TextChannel = None,
            run_forever: bool = False,
            **kwargs  # TODO: This is where session_config gets sent
    ):
        """

        Args:
            voice_channel :class:`discord.VoiceChannel`: The voice channel the session should start playing in.

        Kwargs: 
            run_forever :class:`bool`: Determines whether the session should run forever
            log_channel :class:`discord.TextChannel`: Specifies a channel to log playback history.
        """

        self.bot = bot
        self.config = config
        self.cog = cog
        self.voice_channel = voice_channel

        self.log_channel = log_channel
        self.session_config = kwargs
        self.queue_config = self.session_config.get('queue')

        self.skip_requests = list()
        self.repeat_requests = list()

        self.voice = None
        self.current_track = None

        if run_forever:
            self.queue = Radio(self.queue_config)
        else:
            self.queue = Queue(self.queue_config)

        self.volume = self.session_config.get('default_volume') or float(self.config.hget("config:defaults", "volume"))

        self.is_playing = True
        self.play_next_song = Event()

        create_task(self.session_task())

    @property
    def listeners(self) -> Generator[Member, None, None]:
        """Members listening to this session.

        A member is classified as a listener if:
            - They are not a bot account
            - They are not deafened

        Returns:
            `generator` of `discord.Member`: A generator concisting ow members listening to this session.

        """
        for member in self.voice.channel.members:
            if not member.bot and not (member.voice.deaf or member.voice.self_deaf):
                yield member

    def user_has_permission(self, user: Member) -> bool:
        """Checks if a user has permission to interact with this session."""
        if self.session_config.get("requires_role") is not None:
            return self.session_config.get("requires_role") in user.roles
        return True

    def change_volume(self, volume: float):
        """Changes this session's volume"""
        self.volume = volume
        self.current_track.volume = self.volume

    def toggle_next(self, error=None):
        """Sets the next track to start playing"""
        if error:
            pass
        self.skip_requests.clear()
        # self.repeat_requests.clear()
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def play_track(self):
        """Plays the next track in the queue."""

        # if COG_CONFIG.PLAYING_STATUS_GUILD is not None:  # TODO: Do I want to change status?
        #     if self.voice_channel.guild.id == COG_CONFIG.PLAYING_STATUS_GUILD.id:
        #         activity = Activity(
        #             name=self.current_track.status_information,
        #             type=ActivityType.playing
        #         )
        #
        #         await self.bot.change_presence(activity=activity)

        if self.log_channel is not None:
            await self.log_channel.send(**self.current_track.playing_message)

        self.voice.play(self.current_track, after=self.toggle_next)

    def stop(self):
        """Stops this session."""
        self.is_playing = False
        self.voice.stop()

    def check_listeners(self):
        """Checks if there is anyone listening and pauses / resumes accordingly."""
        if list(self.listeners):
            if self.voice.is_paused():
                self.voice.resume()
        elif self.voice.is_playing():
            self.voice.pause()

    async def session_task(self):

        self.voice = await self.voice_channel.connect()
        self.voice.session = self

        while self.is_playing:
            self.play_next_song.clear()

            # if no more tracks in queue exit
            self.current_track = self.queue.next_track()
            if self.current_track is None:
                self.stop()
                break
            
            # Set volume and play new track
            self.current_track.volume = self.volume
            await self.play_track()
            self.check_listeners()

            # Wait for track to finish before playing next track
            await self.play_next_song.wait()

        # Delete session and disconnect
        del self.cog.sessions[self.voice.guild]  # TODO: Subclass Cog?
        await self.voice.disconnect()
