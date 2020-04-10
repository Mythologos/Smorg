# TODO: documentation

import discord
from discord.ext import commands
from typing import Any, Callable, Iterable, List, Union

from Cogs.Helpers.exceptioner import EmptyEmbed
from Cogs.Helpers.Enumerators.universalist import ColorConstant, DiscordConstant


class Embedder:
    @staticmethod
    async def embed(ctx: commands.Context, sorted_data: List[Any], initialize_embed: Callable,
                    initialize_field: Callable, embed_items: Union[dict, None] = None,
                    field_items: Union[dict, None] = None) -> None:
        enumerated_data: enumerate = enumerate(sorted_data)
        data_embed: discord.Embed = await initialize_embed(**embed_items) if embed_items else await initialize_embed()
        for counter, contents in enumerated_data:
            if counter and (counter % DiscordConstant.MAX_EMBED_FIELDS) == 0:
                await ctx.send(embed=data_embed)
                data_embed = await initialize_embed(**embed_items, page_number=counter) if embed_items \
                    else await initialize_embed(counter)
            if isinstance(contents, Iterable):
                name, value, inline = await initialize_field(*contents, **field_items) if field_items \
                    else await initialize_field(*contents)
            else:
                name, value, inline = await initialize_field(contents, **field_items) \
                    if field_items else await initialize_field(contents)
            data_embed.add_field(name=name, value=value, inline=False)
        else:
            if len(data_embed.fields) == 0:
                raise EmptyEmbed
        await ctx.send(embed=data_embed)

    @staticmethod
    async def initialize_itemized_embed(items: str, color: ColorConstant, page_number: int = 0):
        if not page_number:
            desc: str = f'The {items} supported by Smorg include:'
        else:
            desc = f'Further {items} that Smorg supports consist of:'
        page_number: int = (page_number // DiscordConstant.MAX_EMBED_FIELDS) + 1
        operator_embed: discord.Embed = discord.Embed(
            title=f"Smorg's {items.title()}, Page {page_number}",
            description=desc,
            color=color
        )
        return operator_embed

    @staticmethod
    async def initialize_authored_embed(item_author: str, items: str, color: ColorConstant, page_number: int = 0):
        if not page_number:
            desc: str = f'{items.title()} by {item_author} include:'
        else:
            desc = f'Further {items} by {item_author} consist of:'
        page_number: int = (page_number // DiscordConstant.MAX_EMBED_FIELDS) + 1
        quote_embed: discord.Embed = discord.Embed(
            title=f"The {items.title()} of {item_author}, Page {page_number}",
            description=desc,
            color=color
        )
        return quote_embed
