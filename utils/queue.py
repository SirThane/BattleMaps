
from pathlib import Path
from random import choice

from typing import Optional

from utils.track import Track, MP3Track
from utils.utils import SubRedis


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
        super().__init__(config, queue_config)

        self.playlist_directory = self.queue_config.get("playlist_directory") or \
                                  self.config.hget("config:defaults", "playlist_directory")

    def next_track(self) -> Track:
        mp3_path = choice(list(Path(self.playlist_directory).glob("**/*.mp3")))
        return super().next_track() or MP3Track(mp3_path, self.config)
