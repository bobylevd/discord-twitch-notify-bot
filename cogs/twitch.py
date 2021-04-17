import logging
import datetime

from discord.ext import commands, tasks

from database import r
from twitch_client.twitch_client import TwitchClient
from utils import generate_embed

logger = logging.getLogger()


def _get_game_name(guild, stream):
    return r.hget(f"{guild.id}:{stream.user.login}", "game_name").lower()

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
        logger.info("COG: checking streams")
        for guild in self.client.guilds:
            twitch = TwitchClient(guild.id)
            streams = twitch.live_streams

            channel = self._get_channel(self.channel_ids[guild.id])
            if channel and streams:
                for st in filter(lambda s: s.game_name.lower() == _get_game_name(guild, s), streams):
                    should_notify = False

                    logger.info(f"COG: stream by {st.user.login} is live, checking timestamp")
                    prev_stamp = r.hget(f"{guild.id}:{st.user.login}", "timestamp")
                    if prev_stamp is not None:
                        prev_dt = datetime.datetime.strptime(prev_stamp, "%Y-%m-%dT%H:%M:%S%z")
                        cur_dt = datetime.datetime.strptime(st.started_at, "%Y-%m-%dT%H:%M:%S%z")
                        if (cur_dt - prev_dt) > self.notification_timeout:
                            should_notify = True
                    else:
                        should_notify = True

                    r.hset(f"{guild.id}:{st.user.login}", "timestamp", st.started_at)

                    if should_notify:
                        logger.info(f"COG: sending embed for {st.user.login}")
                        await channel.send(embed=generate_embed(st))

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

    @check.after_loop
    async def after_check(self):
        if self.check.failed() or self.check.is_being_cancelled():
            try:
                self.check.restart()
            except Exception as e:
                logger.error(f"COG: check has failed and unable to restart, {e.__traceback__}")
        logger.info("COG: Loop has finished running")
