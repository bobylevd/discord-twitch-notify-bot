import logging
import datetime

import twitchio
from discord.ext import commands, tasks

from database import r
from twitch_client.twitch_client import TwitchClient
from utils import generate_embed

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

logger = logging.getLogger()


def _get_game_name(guild, stream: twitchio.Stream):
    return r.hget(f"{guild.id}:{stream.user.name.lower()}", "game_name").lower()


class TwitchCheck(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_ids = {}
        self.check.start()
        self.notification_timeout = datetime.timedelta(hours=1)

    def cog_unload(self):
        logger.info("COG: Unload called")
        self.check.cancel()

    @commands.command()
    async def status(self, ctx):
        await ctx.message.add_reaction("👌")

    @tasks.loop(seconds=60.0)
    async def check(self):
        for guild in self.client.guilds:
            twitch = TwitchClient(guild.id)
            streams = await twitch.live_streams()

            if streams:
                channel = self._get_channel(self.channel_ids[guild.id])

                for stream in streams:
                    logger.debug(f"COG: stream by {stream.user.name} is live, checking timestamp")

                    should_notify = False

                    game = _get_game_name(guild, stream)
                    if game and game == stream.game_name.lower():
                        should_notify = self._timestamp_check(guild, stream)
                    elif not game:
                        should_notify = self._timestamp_check(guild, stream)

                    r.hset(
                        f"{guild.id}:{stream.user.name.lower()}",
                        "timestamp",
                        stream.started_at.strftime(TIME_FORMAT)
                    )

                    if should_notify:
                        await self._notify_stream(channel, stream)

    def _timestamp_check(self, guild, stream) -> bool:
        prev_stamp = r.hget(f"{guild.id}:{stream.user.name.lower()}", "timestamp")
        if prev_stamp is not None:
            prev_dt = datetime.datetime.strptime(prev_stamp, TIME_FORMAT)
            cur_dt = stream.started_at
            if (cur_dt - prev_dt) > self.notification_timeout:
                return True
        else:
            return True
        return False

    async def _notify_stream(self, channel, stream):
        logger.info(f"COG: sending embed for {stream.user.name}")
        await channel.send(embed=await generate_embed(stream))

    def _get_channel(self, channel_id=None):
        if channel_id is not None:
            return self.client.get_channel(int(channel_id))
        return None

    @check.before_loop
    async def before_check(self):
        logger.info('waiting for client to get ready...')
        await self.client.wait_until_ready()
        for guild in self.client.guilds:
            self.channel_ids[guild.id] = r.hget(guild.id, "channel_id")
