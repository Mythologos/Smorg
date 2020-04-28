"""
This module holds the quoter Cog. Its functionality revolves around user-supplied quotations.
It consists of three Command objects: quote, immortalize, and yoink.
"""

import discord
from discord.ext import commands
from random import randint
from typing import Union

from Cogs.Helpers.checker import Checker
from Cogs.Helpers.exceptioner import Exceptioner
from Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from smorgasDB import Guild, Quote


class Quoter(commands.Cog, Exceptioner):
    """
    This class centers around quotations and currently has three pertinent Command objects:
    quote, immortalize, and yoink. The first embeds a quote; the second does the same and saves it to Smorg's database;
    the third retrieves a random quotation from the database and displays it.
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description=HelpDescription.QUOTE)
    async def quote(self, ctx: commands.Context, text: str, author: Union[discord.Member, str, None] = None) -> None:
        """
        This method, using the helper method handle_quote(), embeds a supplied quotation with an optional author.

        :param commands.Context ctx: the context from which the command was made.
        :param str text: the actual quotation.
        :param Union[discord.Member, str, None] author: the author of the given quotation, if desired.
        """
        text_author: str = await self.handle_author(author, anonymous_default="An Anonymous Genius")
        await self.handle_quote(ctx, text, text_author, "The Words of ", ColorConstant.DEEP_BLUE)

    @commands.command(description=HelpDescription.IMMORTALIZE)
    async def immortalize(self, ctx: commands.Context, text: str,
                          author: Union[discord.Member, str, None] = None) -> None:
        """
        This method, using the helper method handle_quote(), embeds a supplied quotation with an optional author.
        Then, it saves this quote and author to the database.

        :param commands.Context ctx: the context from which the command was made.
        :param str text: the actual quotation.
        :param Union[discord.Member, str, None] author: the author of the given quotation, if desired.
        """
        text_author: str = await self.handle_author(author, anonymous_default="A True Legend")
        await self.handle_quote(ctx, text, text_author, "The Masterpiece of ", ColorConstant.HEAVENLY_YELLOW)
        Quote.create_quote_with(ctx.guild.id, text, text_author)

    async def handle_quote(self, ctx: commands.Context, text: str, author: Union[discord.Member, str, None],
                           title_without_author: str, color: ColorConstant) -> None:
        """
        This method composes and sends an embed for a quotation and an optional author to a Guild's designated
        quotation channel (or the message's channel if a default channel doesn't exist).

        :param commands.Context ctx: the context from which the command was made.
        :param str text: the actual quotation.
        :param Union[discord.Member, str, None] author: the author of the given quotation, if desired.
        :param str title_without_author: the rest of the Embed's title beyond the author's name.
        :param ColorConstant color: the color of the left side of the Embed.
        """
        current_guild_id: int = ctx.guild.id
        quotation_channel_id: Union[int, None] = Guild.get_quotation_channel_by(current_guild_id)
        current_channel: discord.TextChannel = self.bot.get_channel(quotation_channel_id) or ctx.channel
        quote_response = discord.Embed(
            title=title_without_author + author,
            description=text,
            color=color
        )
        await ctx.message.delete()
        await current_channel.send(embed=quote_response)

    @staticmethod
    async def handle_author(author: Union[discord.Member, str, None], anonymous_default: str) -> str:
        """
        This method determines the author parameter appropriately regardless of how the user gave input to it.

        :param Union[discord.Member, str, None] author:
        :param str anonymous_default: the designated anonymous value of author.
        :return str: the finalized value of author.
        """
        if author:
            if isinstance(author, discord.Member):
                author: str = author.name
            else:
                author = author.strip()
        else:
            author = anonymous_default
        return author

    @commands.command(description=HelpDescription.YOINK)
    @commands.check(Checker.is_yoinkable)
    async def yoink(self, ctx: commands.Context) -> None:
        """
        This method retrieves a random Quote formed by the calling Guild in the database.

        :param commands.Context ctx: the context from which the command was made.
        """
        current_guild_id: int = ctx.guild.id
        maximum: int = Quote.count_quotes(current_guild_id) - 1
        yoinked_quote: Quote = Quote.get_random_quote_by(current_guild_id, randint(0, maximum))
        yoink_response: discord.Embed = discord.Embed(
            title=f'The Legendary Words of {yoinked_quote.author or "A Forgotten Prodigy"}',
            description=yoinked_quote.text,
            color=ColorConstant.HOT_PINK
        )
        await ctx.send(embed=yoink_response)
