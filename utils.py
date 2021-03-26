import os

import discord
import twitch
from twitch.helix import Stream, StreamNotFound

from database.redis_client import r_keys, h_get

helix = twitch.Helix(os.environ['TWITCH_ID'], os.environ['TWITCH_SECRET'])


def get_stream_status(guild_id):
    streams = [s.split(":")[1] for s in r_keys(f"{guild_id}:*")]
    try:
        for stream in helix.streams(user_login=streams):
            if stream.game_name.lower() == h_get(f"{guild_id}:{stream.user.login}", "game_name").lower():
                return stream
    except StreamNotFound:
        return None


def generate_embed(stream: Stream) -> discord.Embed:
    embed = discord.Embed(title=f'{stream.user.login} is now live on twitch',
                          url=f'https://twitch.tv/{stream.user.login}', color=0x00ff00)
    embed.add_field(name='Playing', value=f'{stream.user.stream.game_name}')
    embed.description = f'{stream.user.stream.title}'
    embed.set_thumbnail(url=stream.user.profile_image_url)
    return embed
