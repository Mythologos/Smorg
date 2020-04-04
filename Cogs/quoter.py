# TODO: documentation
# TODO: possibly synthesize quote and immortalize portions to reduce code duplication?
# TODO: maybe change yoink's name to 'fetch'? add other things to it?
# TODO: get a method to display quotes from the database per Guild or per author.
# TODO: re-evaluate the method by which quotes are stored and retrieved per author. How do I want to handle author?
# Can it only be roles? Can it be names? What's the best way to keep everything organized and retrievable?

import discord
from discord.ext import commands
from random import randint
from typing import Union

from smorgasDB import Guild, Quote
from Cogs.Helpers.checker import Checker
from Cogs.Helpers.Enumerators.universalist import ColorConstants, HelpDescriptions


class Quoter(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description=HelpDescriptions.QUOTE)
    async def quote(self, ctx: commands.Context, text: str,
                    author: Union[discord.Member, str, None] = None) -> None:
        """
        This method receives a quotation and embeds it in its quotation chat.
        :param ctx: The context from which the quotation came.
        :param text: a quote to be embedded (a String).
        :param author: TODO: REWRITE
        :return: None.
        """
        quotation_channel_id = Guild.get_quotation_channel_by(ctx.guild.id)
        current_channel = self.bot.get_channel(quotation_channel_id)
        text = text.strip()
        if author:
            if isinstance(author, discord.Member):
                author = author.name
            else:
                author = author.strip()
        quote_response = discord.Embed(
            title=f'The Words of {author if author else "An Anonymous Intellectual"}:',
            description=text,
            color=ColorConstants.DEEP_BLUE
        )
        await ctx.message.delete()
        await current_channel.send(embed=quote_response)

    @quote.error
    async def quote_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Quote): Missing Quotation',
                description='You didn\'t supply a quote.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Quote): Unfinished Quotation',
                description='You forgot a closing quotation mark on your quote or author name.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Quote)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    @commands.command(description=HelpDescriptions.IMMORTALIZE)
    async def immortalize(self, ctx: commands.Context, text: str,
                          author: Union[discord.Member, str, None] = None) -> None:
        """
        This method receives a quotation and embeds it in its quotation chat.
        It also stores this information in the database.
        :param ctx: The context from which the quotation came.
        :param text: a quote to be embedded (a String).
        :param author: TODO: REWRITE
        :return: None.
        """
        current_guild_id = ctx.guild.id
        quotation_channel_id = Guild.get_quotation_channel_by(current_guild_id)
        current_channel = self.bot.get_channel(quotation_channel_id)
        text = text.strip()
        if author:
            if isinstance(author, discord.Member):
                author = author.name
            else:
                author = author.strip()
        quote_response = discord.Embed(
            title=f'The Masterpiece of {author if author else "A True Legend"}:',
            description=text,
            color=ColorConstants.HEAVENLY_YELLOW
        )
        Quote.create_quote_with(current_guild_id, text, author)
        await ctx.message.delete()
        await current_channel.send(embed=quote_response)

    @immortalize.error
    async def immortalize_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        # TODO: add more errors related to engrave's other behavior with the database?
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Immortalize): Missing Quotation',
                description='You didn\'t supply a valid quote.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Immortalize): Unfinished Quotation',
                description='You forgot a closing quotation mark on your quote or author name.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Immortalize)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    # TODO: add Enum for list access values
    @commands.command(description=HelpDescriptions.YOINK)
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
            color=ColorConstants.HOT_PINK
        )
        await ctx.send(embed=yoink_response)

    @yoink.error
    async def yoink_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        if isinstance(error, commands.CheckFailure):
            error_embed = discord.Embed(
                title='Error (Yoink): Invalid Request',
                description='Your server has no quotes.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Yoink)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)
