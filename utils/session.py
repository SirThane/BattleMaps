
# Site
from asyncio import Event
from discord.channel import TextChannel, VoiceChannel
from discord.client import Client
from discord.ext.commands.cog import Cog
from discord.member import Member
from discord.voice_client import VoiceClient
from typing import Generator

# Local
from utils.queue import Queue, Radio
from utils.utils import SubRedis


class Session:

    def __init__(
            self,
            bot: Client,
            config: SubRedis,
            cog: Cog,
            voice: VoiceChannel,
            *,
            log: TextChannel = None,
            run_forever: bool = False,
            **session_config
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
        self.voice_channel = voice

        self.log_channel = log
        self.session_config = session_config
        self.queue_config = self.session_config.get('queue')

        self.skip_requests = list()
        self.repeat_requests = list()

        self.voice = None
        self.current_track = None

        if run_forever:
            self.queue = Radio(config, self.queue_config)
        else:
            self.queue = Queue(config, self.queue_config)

        self.volume = self.session_config.get('default_volume') or float(self.config.hget("config:defaults", "volume"))

        self.is_playing = True
        self.play_next_song = Event()

        # self.bot.loop.create_task(self.session_task())

    @property
    def listeners(self) -> Generator[Member, None, None]:
        """Members listening to this session.

        A member is classified as a listener if:
            - They are not a bot account
            - They are not deafened

        Returns:
            `generator` of `discord.Member`: A generator consisting ow members listening to this session.

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
        if self.log_channel:
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

        self.voice: VoiceClient = await self.voice_channel.connect()
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
