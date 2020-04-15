# TODO: documentation
# TODO: maybe change yoink's name to 'fetch'? add other things to it?

import discord
from discord.ext import commands
from random import randint
from typing import Union

from Cogs.Helpers.checker import Checker
from Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from smorgasDB import Guild, Quote


class Quoter(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description=HelpDescription.QUOTE)
    async def quote(self, ctx: commands.Context, text: str, author: Union[discord.Member, str, None] = None) -> None:
        text_author: str = await self.handle_author(author, "An Anonymous Genius")
        await self.handle_quote(ctx, text, text_author, "The Words of ", ColorConstant.DEEP_BLUE)

    @quote.error
    async def quote_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Quote): Missing Quotation',
                description='You didn\'t supply a quote.',
                color=ColorConstant.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Quote): Unfinished Quotation',
                description='You forgot a closing quotation mark on your quote or author name.',
                color=ColorConstant.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Quote)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstant.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    @commands.command(description=HelpDescription.IMMORTALIZE)
    async def immortalize(self, ctx: commands.Context, text: str,
                          author: Union[discord.Member, str, None] = None) -> None:
        text_author: str = await self.handle_author(author, "A True Legend")
        await self.handle_quote(ctx, text, text_author, "The Masterpiece of ", ColorConstant.HEAVENLY_YELLOW)
        Quote.create_quote_with(ctx.guild.id, text, text_author)

    @immortalize.error
    async def immortalize_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        # TODO: add more errors related to immortalize's other behavior with the database?
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Immortalize): Missing Quotation',
                description='You didn\'t supply a valid quote.',
                color=ColorConstant.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Immortalize): Unfinished Quotation',
                description='You forgot a closing quotation mark on your quote or author name.',
                color=ColorConstant.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Immortalize)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstant.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    async def handle_quote(self, ctx: commands.Context, text: str, author: Union[discord.Member, str, None],
                           title_without_author: str, color: ColorConstant):
        current_guild_id: int = ctx.guild.id
        quotation_channel_id: int = Guild.get_quotation_channel_by(current_guild_id)
        current_channel: discord.TextChannel = self.bot.get_channel(quotation_channel_id)
        quote_response = discord.Embed(
            title=title_without_author + author,
            description=text,
            color=color
        )
        await ctx.message.delete()
        await current_channel.send(embed=quote_response)

    @staticmethod
    async def handle_author(author: Union[discord.Member, str, None], anonymous_default: str):
        if author:
            if isinstance(author, discord.Member):
                author = author.name
            else:
                author = author.strip()
        else:
            author = anonymous_default
        return author

    # TODO: add Enum for list access values
    @commands.command(description=HelpDescription.YOINK)
    @commands.check(Checker.is_yoinkable)
    async def yoink(self, ctx: commands.Context) -> None:
        """
        This method retrieves a random Quote formed by the calling Guild in the database.
        It also lets the user know whether a Quote even exists.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        current_guild_id = ctx.guild.id
        maximum = Quote.count_quotes(current_guild_id) - 1
        yoinked_quote = Quote.get_random_quote_by(current_guild_id, randint(0, maximum))
        author = yoinked_quote[0] if yoinked_quote[0] else 'A Forgotten Prodigy'
        yoink_response = discord.Embed(
            title=f'The Legendary Words of {author}',
            description=yoinked_quote[1],
            color=ColorConstant.HOT_PINK
        )
        await ctx.send(embed=yoink_response)

    @yoink.error
    async def yoink_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        if isinstance(error, commands.CheckFailure):
            error_embed = discord.Embed(
                title='Error (Yoink): Invalid Request',
                description='Your server has no quotes.',
                color=ColorConstant.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Yoink)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstant.ERROR_RED
            )
        await ctx.send(embed=error_embed)
