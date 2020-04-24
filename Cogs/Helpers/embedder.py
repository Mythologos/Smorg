# TODO: documentation

import discord
from typing import Any, Callable, Iterable, List, Union

from Cogs.Helpers.exceptioner import EmptyEmbed
from Cogs.Helpers.Enumerators.universalist import ColorConstant, DiscordConstant


class Embedder:
    @staticmethod
    async def embed(destination_channel: discord.TextChannel, sorted_data: List[Any], initialize_embed: Callable,
                    initialize_field: Callable, embed_items: Union[dict, None] = None,
                    field_items: Union[dict, None] = None) -> None:
        if not embed_items:
            embed_items = {}
        if not field_items:
            field_items = {}
        enumerated_data: enumerate = enumerate(sorted_data)
        data_embed: discord.Embed = await initialize_embed(**embed_items)
        for counter, contents in enumerated_data:
            embed_items.update({'page_number': (counter // DiscordConstant.MAX_EMBED_FIELDS) + 1})
            if field_items and 'counter' in field_items:
                field_items.update({'counter': counter})
            if counter and (counter % DiscordConstant.MAX_EMBED_FIELDS) == 0:
                await destination_channel.send(embed=data_embed)
                data_embed = await initialize_embed(**embed_items)
            if isinstance(contents, Iterable):
                name, value, inline = await initialize_field(*contents, **field_items)
            else:
                name, value, inline = await initialize_field(contents, **field_items)
            data_embed.add_field(name=name, value=value, inline=False)
        else:
            if len(data_embed.fields) == 0:
                raise EmptyEmbed
        await destination_channel.send(embed=data_embed)

    @staticmethod
    async def initialize_itemized_embed(items: str, color: ColorConstant, page_number: int = 1) -> discord.Embed:
        if page_number == 1:
            desc: str = f'The {items} supported by Smorg include:'
        else:
            desc = f'Further {items} that Smorg supports consist of:'
        itemized_embed: discord.Embed = discord.Embed(
            title=f"Smorg's {items.title()}, Page {page_number}",
            description=desc,
            color=color
        )
        return itemized_embed

    @staticmethod
    async def initialize_authored_embed(item_author: str, items: str, color: ColorConstant,
                                        page_number: int = 1) -> discord.Embed:
        if page_number == 1:
            desc: str = f'{items.title()} by {item_author} include:'
        else:
            desc = f'Further {items} by {item_author} consist of:'
        authored_embed: discord.Embed = discord.Embed(
            title=f"The {items.title()} of {item_author}, Page {page_number}",
            description=desc,
            color=color
        )
        return authored_embed
