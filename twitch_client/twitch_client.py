import logging
import os

import twitch
from twitch.helix import StreamNotFound

from database import r

logger = logging.getLogger()


class TwitchClient:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.helix = twitch.Helix(os.environ['TWITCH_ID'], os.environ['TWITCH_SECRET'])

    @property
    def streamers(self):
        return [s.split(":")[1] for s in r.keys(f"{self.guild_id}:*")]

    @property
    def live_streams(self):
        """
        Return active streams if any
        :return: `twitch_client.helix.resources.Streams`
        """
        try:
            streams = self.helix.streams(user_login=self.streamers)
            return streams
        except StreamNotFound:
            logger.debug("No streams found")
            return None
