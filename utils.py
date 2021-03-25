import os

import discord
import redis
import twitch
from twitch.helix import Stream


helix = twitch.Helix(os.environ['TWITCH_ID'], os.environ['TWITCH_SECRET'])


r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    password=os.environ["REDIS_PASSWORD"],
    ssl=True,
    decode_responses=True
)


def get_stream_status():
    for stream in helix.streams(user_login=r.keys("*")):
        if stream.game_name.lower() == r.hget(stream.user.login, "game_name").lower():
            return stream
    return None


def generate_embed(stream: Stream) -> discord.Embed:
    embed = discord.Embed(title=f'{stream.user.login} is now live on twitch',
                          url=f'https://twitch.tv/{stream.user.login}', color=0x00ff00)
    embed.add_field(name='Playing', value=f'{stream.user.stream.game_name}')
    embed.description = f'{stream.user.stream.title}'
    embed.set_thumbnail(url=stream.user.profile_image_url)
    return embed
