import logging

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

    def cog_unload(self):
        self.check.cancel()

    @commands.command()
    async def status(self, ctx):
        await ctx.message.add_reaction("👌")

    @tasks.loop(seconds=15.0)
    async def check(self):
        logger.info("COG: checking streams")
        for guild in self.client.guilds:
            twitch = TwitchClient(guild.id)
            streams = twitch.live_streams

            channel = self._get_channel(self.channel_ids[guild.id])
            if channel and streams:
                for st in filter(lambda s: s.game_name.lower() == _get_game_name(guild, s), streams):
                    logger.info(f"COG: stream by {st.user.login} is live, checking timestamp")
                    if st.started_at != r.hget(f"{guild.id}:{st.user.login}", "timestamp"):
                        r.hset(f"{guild.id}:{st.user.login}", "timestamp", st.started_at)
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
