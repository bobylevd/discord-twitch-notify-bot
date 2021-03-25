import datetime
import logging

from discord.ext import commands, tasks

from database.redis_client import get_stream, set_stream
from utils import get_stream_status, generate_embed

logger = logging.getLogger()

TIME_FORMAT = "%m/%d/%Y, %H:%M:%S"


class TwitchCheck(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check.start()

    def cog_unload(self):
        self.check.cancel()

    @tasks.loop(minutes=10.0)
    async def check(self):
        stream = get_stream_status()
        if stream:
            channel = self.client.get_channel(int(get_stream(stream, "channel_id")))
            curr_time = datetime.datetime.utcnow()
            timedelta = datetime.timedelta(hours=4)
            next_check = curr_time + timedelta

            def timestamp(stream):
                ts = get_stream(stream, "timestamp")
                return ts if ts else curr_time.strftime(TIME_FORMAT)

            if curr_time >= datetime.datetime.strptime(timestamp(stream), TIME_FORMAT):
                if channel:
                    await channel.send(embed=generate_embed(stream))
                    set_stream(stream, "timestamp", next_check.strftime(TIME_FORMAT))

    @check.before_loop
    async def before_check(self):
        logger.info('waiting for client to get ready...')
        await self.client.wait_until_ready()
