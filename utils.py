import os

import discord
import twitch
from twitch.helix import Stream

from database.redis_client import all_keys, get_stream

helix = twitch.Helix(os.environ['TWITCH_ID'], os.environ['TWITCH_SECRET'])


def get_stream_status():
    for stream in helix.streams(user_login=all_keys()):
        if stream.game_name.lower() == get_stream(stream, "game_name"):
            return stream
    return None


def generate_embed(stream: Stream) -> discord.Embed:
    embed = discord.Embed(title=f'{stream.user.login} is now live on twitch',
                          url=f'https://twitch.tv/{stream.user.login}', color=0x00ff00)
    embed.add_field(name='Playing', value=f'{stream.user.stream.game_name}')
    embed.description = f'{stream.user.stream.title}'
    embed.set_thumbnail(url=stream.user.profile_image_url)
    return embed
