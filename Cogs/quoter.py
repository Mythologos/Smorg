# TODO: documentation
# TODO: add enumerator for embed colors

import discord
from discord.ext import commands
from random import randint
from smorgasDB import Guild, Quote
from Cogs.Helpers.checker import Checker
from Cogs.Helpers.Enumerators.universalist import ColorConstants


class Quoter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='This command embeds a quote. It takes a quote (in quotation marks) ' +
                                  'and, optionally, an author as arguments.')
    async def quote(self, ctx, text, author='An Anonymous Intellectual'):
        """
        This method receives a quotation and embeds it in its quotation chat.
        :param ctx: The context from which the quotation came.
        :param text: a quote to be embedded (a String).
        :param author: the name of the author of the quote (a String).
        :return: None.
        """
        quotation_channel_id = Guild.get_quotation_channel_by(ctx.guild.id)
        current_channel = self.bot.get_channel(quotation_channel_id)
        text = text.strip()
        quote_response = discord.Embed(
            title=f'The Marvelous Brainchild of {author}:',
            description=text,
            color=0x20409A
        )
        await ctx.message.delete()
        await current_channel.send(embed=quote_response)

    @quote.error
    async def quote_error(self, ctx, error):
        error_embed = discord.Embed()
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

    @commands.command(description='This command embeds a quote and stores it for posterity\'s sake. ' +
                                  'It takes a quote (in quotation marks) and, optionally, an author as arguments.')
    async def sanctify(self, ctx, text='', author=None):
        """
        This method receives a quotation and embeds it in its quotation chat.
        It also stores this information in the database.
        :param ctx: The context from which the quotation came.
        :param text: a quote to be embedded (a String).
        :param author: the name of the author of the quote (a String).
        :return: None.
        """
        current_guild_id = ctx.guild.id
        quotation_channel_id = Guild.get_quotation_channel_by(current_guild_id)
        current_channel = self.bot.get_channel(quotation_channel_id)
        text = text.strip()
        quote_response = discord.Embed(
            title=f'The Holiest Opus of {author if author else "An Unknowable Deity"}:',
            description=text,
            color=0xFDF06F
        )
        Quote.create_quote_with(current_guild_id, text, author)
        await ctx.message.delete()
        await current_channel.send(embed=quote_response)

    @sanctify.error
    async def sanctify_error(self, ctx, error):
        error_embed = discord.Embed()
        # TODO: add more errors related to sanctify's other behavior with the database?
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Sanctify): Missing Quotation',
                description='You didn\'t supply a valid quote.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Sanctify): Unfinished Quotation',
                description='You forgot a closing quotation mark on your quote or author name.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Sanctify)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    # TODO: add Enum for list access values
    @commands.command(description='This command retrieves and displays a random stored quote.')
    @commands.check(Checker.is_yoinkable)
    async def yoink(self, ctx):
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
            color=0xEE104E
        )
        await ctx.send(embed=yoink_response)

    @yoink.error
    async def yoink_error(self, ctx, error):
        error_embed = discord.Embed()
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
