# TODO: documentation

import discord
from discord.ext import commands
from typing import Any, Callable, Iterable, List, Union

from Cogs.Helpers.exceptioner import EmptyEmbed
from Cogs.Helpers.Enumerators.universalist import DiscordConstants


class Embedder:
    @staticmethod
    async def embed(ctx: commands.Context, sorted_data: List[Any], initialize_embed: Callable,
                    initialize_field: Callable, embed_items: Union[dict, None] = None,
                    field_items: Union[dict, None] = None) -> None:
        enumerated_data: enumerate = enumerate(sorted_data)
        data_embed: discord.Embed = await initialize_embed(**embed_items) if embed_items else await initialize_embed()
        for counter, contents in enumerated_data:
            if counter and (counter % DiscordConstants.MAX_EMBED_FIELDS) == 0:
                await ctx.send(embed=data_embed)
                data_embed = await initialize_embed(**embed_items, page_number=counter) if embed_items \
                    else await initialize_embed(counter)
            if isinstance(contents, Iterable):
                name, value, inline = await initialize_field(*contents, **field_items) if field_items \
                    else await initialize_field(*contents)
            else:
                name, value, inline = await initialize_field(contents, **field_items) \
                    if isinstance(contents, Iterable) else await initialize_field(contents)
            data_embed.add_field(name=name, value=value, inline=False)
        else:
            if len(data_embed.fields) == 0:
                raise EmptyEmbed
        await ctx.send(embed=data_embed)
