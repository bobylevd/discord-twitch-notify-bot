import logging
import os
from typing import List

import twitchio

from database import r

logger = logging.getLogger()
twitch_io_client = twitchio.Client.from_client_credentials(os.environ['TWITCH_ID'], os.environ['TWITCH_SECRET'], )


class TwitchClient:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.api_client = twitch_io_client

    @property
    def streamers(self):
        return [s.split(":")[1] for s in r.keys(f"{self.guild_id}:*")]

    async def live_streams(self) -> List[twitchio.Stream]:
        """
        Return active streams if any
        :return: `twitch_client.helix.resources.Streams`
        """

        if not self.streamers:
            return []
        streams = await self.api_client.fetch_streams(user_logins=self.streamers)
        if not streams:
            logger.debug("No streams found")
        return streams
