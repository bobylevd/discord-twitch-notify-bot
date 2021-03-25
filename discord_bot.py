import logging
import os
import sys

import discord
from discord.ext import commands

from cogs.twitch import TwitchCheck
from utils import r

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()


intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', description="bot command", intents=intents)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}/{bot.user.id}')


@bot.command()
async def add(ctx, streamer_name, game_name):
    logger.info(f"adding streamer {streamer_name}, with game {game_name}")
    r.hset(streamer_name.lower(), "game_name", game_name)
    r.hset(streamer_name.lower(), "guild_id", ctx.guild.id)
    r.hset(streamer_name.lower(), "channel_id", ctx.channel.id)
    await ctx.send(f"Streamer {streamer_name} was added to watch list")


@bot.command()
async def remove(ctx, streamer_name):
    for k in r.hkeys(streamer_name.lower()):
        logger.debug(f"removing key {k} from {streamer_name}")
        r.hdel(streamer_name.lower(), k)
    await ctx.send(f"Streamer {streamer_name} was removed from watch list")


bot.add_cog(TwitchCheck(bot))
bot.run(os.environ['DISCORD_TOKEN'])
