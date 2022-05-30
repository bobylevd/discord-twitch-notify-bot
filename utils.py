import logging

import discord
from twitchio import Stream, User

logger = logging.getLogger()


async def generate_embed(stream: Stream) -> discord.Embed:
    embed = discord.Embed(title=f'{stream.user.name} is now live on twitch',
                          url=f'https://twitch.tv/{stream.user.name.lower()}', color=0x00ff00)
    embed.add_field(name='Playing', value=f'{stream.game_name}')
    embed.description = f'{stream.title}'
    full_user: User = await stream.user.fetch()
    embed.set_thumbnail(url=full_user.profile_image)
    return embed
