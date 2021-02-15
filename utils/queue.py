
# Lib
from pathlib import Path
from random import choice

# Site
from typing import Optional

# Local
from utils.track import Track, MP3Track
from utils.classes import SubRedis


class Queue:

    def __init__(self, config: SubRedis, queue_config=None):
        self.config = config
        self.queue_config = queue_config or dict()
        self.requests = list()

    def next_track(self) -> Optional[Track]:
        if self.requests:
            return self.requests.pop(0)

    def add_request(self, track: Track):
        """Adds a track to the list of requests.

        Args:
            track (Track): The track to add to the requests pool.

        """
        self.requests.append(track)


class Radio(Queue):

    def __init__(self, config: SubRedis, queue_config=None):
        self.config = config
        super().__init__(config, queue_config)

        playlist = self.queue_config.get("playlist_directory")
        if playlist:
            self.playlist_directory = playlist
        else:
            self.playlist_directory = self.config.hget("config:defaults", "playlist_directory")

    def next_track(self) -> Track:

        queue_next = super().next_track()
        if queue_next:
            return queue_next
        else:
            mp3_path = choice(list(Path(self.playlist_directory).glob("**/*.mp3")))
            return MP3Track(mp3_path, self.config)
