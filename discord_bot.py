import logging
import os
import sys

import discord
from discord.ext import commands

from cogs.twitch import TwitchCheck
from database.redis_client import h_set, r_get_keys, r_del_keys, r_keys, h_get

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
    h_set(f"{ctx.guild.id}", "channel_id", ctx.channel.id)
    h_set(f"{ctx.guild.id}:{streamer_name.lower()}", "game_name", game_name)
    await ctx.message.add_reaction('✅')


@bot.command()
async def remove(ctx, streamer_name):
    logger.info(f"removing streamer {streamer_name}")
    r_del_keys(f"{ctx.guild.id}:{streamer_name.lower()}", *r_get_keys(f"{ctx.guild.id}:{streamer_name.lower()}"))
    await ctx.message.add_reaction('☠')
    await ctx.message.add_reaction('✅')


@bot.command()
async def list_all(ctx):
    logger.info(f"requested all streamers info")
    await ctx.send("Currently tracking:")
    for s in [s.split(":")[1] for s in r_keys(f"{ctx.guild.id}:*")]:
        await ctx.send(f"{s} - {h_get(f'{ctx.guild.id}:{s}', 'game_name')}")


bot.add_cog(TwitchCheck(bot))
bot.run(os.environ['DISCORD_TOKEN'])
