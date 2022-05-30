import logging
import os
import sys

import discord
from discord.ext import commands

from cogs.twitch import TwitchCheck
from database import r

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()


intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', description="bot command", intents=intents)


@bot.event
async def on_ready():
    logger.info(f'BOT: Logged in as {bot.user.name}/{bot.user.id}')


@bot.command()
async def add(ctx, streamer_name, game_name=""):
    logger.info(f"BOT: adding streamer {streamer_name}, with game {game_name}")
    r.hset(f"{ctx.guild.id}", "channel_id", ctx.channel.id)
    r.hset(f"{ctx.guild.id}:{streamer_name.lower()}", "game_name", game_name)
    await ctx.message.add_reaction('✅')


@bot.command()
async def remove(ctx, streamer_name):
    logger.info(f"BOT: removing streamer {streamer_name}")
    r.hdel(f"{ctx.guild.id}:{streamer_name.lower()}", *r.hkeys(f"{ctx.guild.id}:{streamer_name.lower()}"))
    await ctx.message.add_reaction('☠')
    await ctx.message.add_reaction('✅')


@bot.command()
async def list_all(ctx):
    logger.info(f"BOT: requested all streamers info")
    streams = [s.split(":")[1] for s in r.keys(f"{ctx.guild.id}:*")]
    message = f"Currently tracking: {streams}"
    await ctx.send(message)


@bot.command()
async def add_stream_id(ctx, stream_id):
    logger.info("BOT: Add stream id to db")
    r.hset(f"{ctx.guild.id}", "stream_id", stream_id)
    await ctx.message.add_reaction('✅')


@bot.command()
async def stream_id(ctx):
    stream_id = r.hget(f"{ctx.guild.id}", "stream_id")
    await ctx.send(stream_id)


bot.add_cog(TwitchCheck(bot))
bot.run(os.environ['DISCORD_TOKEN'])
