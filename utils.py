import logging

import discord
from twitch.helix import Stream

logger = logging.getLogger()


def generate_embed(stream: Stream) -> discord.Embed:
    embed = discord.Embed(title=f'{stream.user.login} is now live on twitch',
                          url=f'https://twitch.tv/{stream.user.login}', color=0x00ff00)
    embed.add_field(name='Playing', value=f'{stream.user.stream.game_name}')
    embed.description = f'{stream.user.stream.title}'
    embed.set_thumbnail(url=stream.user.profile_image_url)
    return embed
