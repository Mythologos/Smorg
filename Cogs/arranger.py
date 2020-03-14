import discord
from discord.ext import commands
from Cogs.Helpers.Enumerators.universalist import ColorConstants
from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator


class Arranger(commands.Cog, Disambiguator):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(description='This command tells Smorg what channel in which it should perform some task. ' +
                                'It takes a the type of channel (e.g. quotation, reminder), the channel\'s name, ' +
                                'and, if the channel has the same name as other channels, ' +
                                'the number of the instance of the channel as an argument.')
    async def govern(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title='Error (Govern): Missing Domain',
                description='You didn\'t supply a domain.',
                color=ColorConstants.ERROR_RED
            ))

    @govern.command()
    async def quotation(self, ctx, channel_name):
        """
        This method allows users to alter the chat in which Smorg embeds its quotes.
        :param ctx: The context from which the request came.
        :param channel_name: The name of the channel which the user wants to designate as Smorg's quotation domain.
        If channels have the same name, Disambiguator derives order from counting Discord channels from top to bottom.
        :return: None.
        """
        govern_message = 'Congrats! You have successfully changed where I engrave your greatest sayings.'
        await self.handle_domain(ctx, Guild.update_quotation_channel, govern_message, channel_name)

    @govern.command()
    async def reminder(self, ctx, channel_name):
        """
        This method allows users to alter the chat in which Smorg posts its reminders.
        :param ctx: The context from which the request came.
        :param channel_name: The name of the channel which the user wants to designate as Smorg's reminder domain.
        If channels have the same name, Disambiguator derives order from counting Discord channels from top to bottom.
        :return: None.
        """
        govern_message = 'Congrats! You have successfully changed where I blare your noisiest pings.'
        await self.handle_domain(ctx, Guild.update_reminder_channel, govern_message, channel_name)

    @govern.command()
    async def gamble(self, ctx, channel_name):
        """
        This method allows users to alter the chat in which Smorg posts its public gambles.
        :param ctx: The context from which the request came.
        :param channel_name: The name of the channel which the user wants to designate as Smorg's gamble domain.
        If channels have the same name, Disambiguator derives order from counting Discord channels from top to bottom.
        :return: None.
        """
        govern_message = 'Congrats! You have successfully changed where you let the cards and dice fly.'
        await self.handle_domain(ctx, Guild.update_gamble_channel, govern_message, channel_name)

    # TODO: figure out documentation situation between this and the three methods above.
    async def handle_domain(self, ctx, table_update_method, govern_message, channel_name):
        current_guild = ctx.guild
        valid_channels: list = [channel for channel in current_guild.text_channels if channel.name == channel_name]
        if not valid_channels:
            raise commands.UserInputError()
        else:
            channel_index: int = await Disambiguator.disambiguate(self.bot, ctx, valid_channels)
            table_update_method(current_guild.id, valid_channels[channel_index].id)
        await self.bot.get_channel(valid_channels[channel_index].id).send(govern_message)

    @quotation.error
    @reminder.error
    @gamble.error
    async def domain_error(self, ctx, error):
        error_embed = discord.Embed()
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Govern): Missing Channel',
                description='You didn\'t supply a channel.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Govern): Unfinished Channel Quotation',
                description='You forgot a closing quotation mark on your channel name.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.UserInputError):
            error_embed = discord.Embed(
                title='Error (Govern): Invalid Channel',
                description='The channel name given was not found.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Govern)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)
