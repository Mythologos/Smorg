"""
This module contains the Embedder class, a widely-used mix-in that helps various Cogs in Smorg produce embeds.
"""

from discord import TextChannel, Embed
from typing import Any, Callable, Iterable, List, Union

from .exceptioner import EmptyEmbed
from .Enumerators.universalist import ColorConstant, DiscordConstant


class Embedder:
    """
    This class is a mix-in that contains helper methods for creating embeds.
    It also contains two template methods for fashioning the overall Embed objects.
    """
    @staticmethod
    async def embed(destination_channel: TextChannel, sorted_data: List[Any], initialize_embed: Callable,
                    initialize_field: Callable, embed_items: Union[dict, None] = None,
                    field_items: Union[dict, None] = None) -> None:
        """
        This method produces Discord Embeds of varying kinds and sends them to a given channel.
        It accepts functions to produce the overall Embed and its fields for data sets of varying sizes,
        taking two optional dictionaries to add to each function's customization.

        :param TextChannel destination_channel: the channel to which the Embed will be posted.
        :param List[Any] sorted_data: the data which will fill up the Embed's fields, pre-sorted.
        :param Callable initialize_embed: the function that initializes each Embed;
        it should be adaptive to producing multiple Embeds.
        :param Callable initialize_field: the function that initializes each field for each Embed;
        it should produce a tuple of items that represent the field's name, value, and a determination
        as to whether it will be inline with the other fields or not.
        :param Union[dict, None] embed_items: the additional items that are necessary to process
        the initialize_embed function, set up as keyword arguments.
        :param Union[dict, None] field_items: the additional items that are necessary to process
        the initialize_field function, set up as keyword arguments.
        """
        if not embed_items:
            embed_items = {}
        if not field_items:
            field_items = {}
        enumerated_data: enumerate = enumerate(sorted_data)
        data_embed: Embed = await initialize_embed(**embed_items)
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
    async def initialize_itemized_embed(items: str, color: ColorConstant, page_number: int = 1) -> Embed:
        """
        This method initializes an Embed that has a certain kind of item at its core.
        It is a kind of Embed creation template, as it can be employed flexibly for various data sets.

        :param str items: the major entities (pluralized) which the Embed concerns.
        :param ColorConstant color: the color that the Embed should be.
        :param int page_number: the number indicating that the nth Embed is being created.
        :return Embed: an Embed used to store and to output information on a certain set of items.
        """
        if page_number == 1:
            desc: str = f'The {items} supported by Smorg include:'
        else:
            desc = f'Further {items} that Smorg supports consist of:'
        itemized_embed: Embed = Embed(
            title=f"Smorg's {items.title()}, Page {page_number}",
            description=desc,
            color=color
        )
        return itemized_embed

    @staticmethod
    async def initialize_authored_embed(item_author: str, items: str, color: ColorConstant, page_number: int = 1) \
            -> Embed:
        """
        This method initializes an Embed that has a certain kind of item authored by some named thing at its core.
        It is a kind of Embed creation template, as it can be employed flexibly for various data sets.

        :param str item_author: the author of the entities which the Embed concerns.
        :param str items: the major entities (pluralized) which the Embed concerns.
        :param ColorConstant color: the color that the Embed should be.
        :param int page_number: the number indicating that the nth Embed is being created.
        :return Embed: an Embed used to store and to output information on a certain set of authored items.
        """
        if page_number == 1:
            desc: str = f'{items.title()} by {item_author} include:'
        else:
            desc = f'Further {items} by {item_author} consist of:'
        authored_embed: Embed = Embed(
            title=f"The {items.title()} of {item_author}, Page {page_number}",
            description=desc,
            color=color
        )
        return authored_embed
