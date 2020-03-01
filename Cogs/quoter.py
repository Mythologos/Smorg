import discord
from discord.ext import commands
import random
from smorgasDB import Guild, Quote


class Quoter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='This command embeds a quote. It takes a quote (in quotation marks) ' +
                                  'and, optionally, an author as arguments.')
    async def quote(self, ctx, text='', author='An Anonymous Intellectual'):
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
        if text:
            quote_response = discord.Embed(title=f'The Marvelous Brainchild of {author}:',
                                           description=text,
                                           color=0x20409A)
            await ctx.message.delete()
        else:
            quote_response = discord.Embed(title='Error (Quote): Invalid Quotation',
                                           description='You didn\'t supply a valid quote.',
                                           color=0xB80000)
        await current_channel.send(embed=quote_response)

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
        if text:
            quote_response = discord.Embed(title=f'The Holiest Opus of {author if author else "An Unknowable Deity"}:',
                                           description=text, color=0xFDF06F)
            Quote.create_quote_with(current_guild_id, text, author)
            await ctx.message.delete()
        else:
            quote_response = discord.Embed(title='Error (Sanctify): Invalid Quotation',
                                           description='You didn\'t supply a valid quote.',
                                           color=0xB80000)
        await current_channel.send(embed=quote_response)

    @commands.command(description='This command retrieves and displays a random stored quote.')
    async def yoink(self, ctx):
        """
        This method retrieves a random Quote formed by the calling Guild in the database.
        It also lets the user know whether a Quote even exists.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        current_guild_id = ctx.guild.id
        maximum = Quote.count_quotes(current_guild_id) - 1
        if maximum >= 0:
            yoinked_quote = Quote.get_random_quote_by(current_guild_id, random.randint(0, maximum))
            author = yoinked_quote[0] if yoinked_quote[0] else 'A Forgotten Prodigy'
            yoink_response = discord.Embed(title=f'The Legendary Words of {author}',
                                           description=yoinked_quote[1],
                                           color=0xEE104E)
        else:
            yoink_response = discord.Embed(title='Error (Yoink): Invalid Request',
                                           description='Your server has no quotes.',
                                           color=0xB80000)
        await ctx.send(embed=yoink_response)
