import logging
from datetime import datetime, timedelta

from discord.ext import commands, tasks

from database.redis_client import h_get, h_set
from utils import get_stream_status, generate_embed

logger = logging.getLogger()


class TwitchCheck(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check.start()

    def cog_unload(self):
        self.check.cancel()

    @tasks.loop(minutes=1.0)
    async def check(self):
        now = datetime.now()
        skip_until = now + timedelta(hours=6)
        now_ts = now.timestamp()
        skip_until_ts = skip_until.timestamp()

        for guild in self.client.guilds:
            streams = get_stream_status(guild.id)
            if h_get(guild.id, "channel_id") is not None:
                channel = self.client.get_channel(int(h_get(guild.id, "channel_id")))
                if streams:
                    for s in streams:
                        logger.info(f"found stream by {s.user.login}")
                        if not h_get(f"{guild.id}:{s.user.login}", "timestamp"):
                            logger.info(f"stream {s.user.login} has no timestamp, setting to {now_ts}")
                            h_set(f"{guild.id}:{s.user.login}", "timestamp", now_ts)
                        if now_ts >= float(h_get(f"{guild.id}:{s.user.login}", "timestamp")):
                            h_set(f"{guild.id}:{s.user.login}", "timestamp", skip_until_ts)
                            logger.info(f"able to send notification, updating timestamp from {now_ts} to {skip_until_ts}")
                            await channel.send(embed=generate_embed(s))

    @check.before_loop
    async def before_check(self):
        logger.info('waiting for client to get ready...')
        await self.client.wait_until_ready()
