import logging
import os
import sys

import discord
from discord.ext import commands

from cogs.twitch import TwitchCheck
from database.redis_client import r_set, r_get_keys, r_del_keys, all_keys, r_get

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
    r_set(streamer_name, "game_name", game_name)
    r_set(streamer_name, "guild_id", str(ctx.guild.id))
    r_set(streamer_name, "channel_id", str(ctx.channel.id))
    await ctx.send(f"Streamer {streamer_name} was added to watch list")


@bot.command()
async def remove(ctx, streamer_name):
    logger.info(f"removing streamer {streamer_name}")
    r_del_keys(streamer_name, *r_get_keys(streamer_name))
    await ctx.send(f"Streamer {streamer_name} was removed from watch list")


@bot.command()
async def list_all(ctx):
    logger.info(f"requested all streamers info")
    streamers = all_keys()
    await ctx.send("Currently tracking:")
    for s in streamers:
        await ctx.send(f"{s} - {r_get(s, 'game_name')}")


bot.add_cog(TwitchCheck(bot))
bot.run(os.environ['DISCORD_TOKEN'])
