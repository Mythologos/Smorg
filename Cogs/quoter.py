"""
...
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
    ...
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description=HelpDescription.QUOTE)
    async def quote(self, ctx: commands.Context, text: str, author: Union[discord.Member, str, None] = None) -> None:
        """
        ...

        :param commands.Context ctx: the context from which the command was made.
        :param str text:
        :param Union[discord.Member, str, None] author:
        """
        text_author: str = await self.handle_author(author, anonymous_default="An Anonymous Genius")
        await self.handle_quote(ctx, text, text_author, "The Words of ", ColorConstant.DEEP_BLUE)

    @commands.command(description=HelpDescription.IMMORTALIZE)
    async def immortalize(self, ctx: commands.Context, text: str,
                          author: Union[discord.Member, str, None] = None) -> None:
        """
        ...

        :param commands.Context ctx: the context from which the command was made.
        :param str text:
        :param Union[discord.Member, str, None] author:
        """
        text_author: str = await self.handle_author(author, anonymous_default="A True Legend")
        await self.handle_quote(ctx, text, text_author, "The Masterpiece of ", ColorConstant.HEAVENLY_YELLOW)
        Quote.create_quote_with(ctx.guild.id, text, text_author)

    async def handle_quote(self, ctx: commands.Context, text: str, author: Union[discord.Member, str, None],
                           title_without_author: str, color: ColorConstant) -> None:
        """
        ...

        :param commands.Context ctx: the context from which the command was made.
        :param str text:
        :param Union[discord.Member, str, None] author:
        :param str title_without_author:
        :param ColorConstant color:
        """
        current_guild_id: int = ctx.guild.id
        quotation_channel_id: Union[int, None] = Guild.get_quotation_channel_by(current_guild_id)
        current_channel: discord.TextChannel = self.bot.get_channel(quotation_channel_id) or ctx.message.channel
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
        ...
        :param Union[discord.Member, str, None] author:
        :param str anonymous_default:
        :return str:
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
