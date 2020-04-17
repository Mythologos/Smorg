# TODO: documentation

import discord
from discord.ext import commands

from Cogs.Helpers.Enumerators.universalist import ColorConstant
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, \
    InvalidMonth, InvalidTimeZone, InvalidYear, MissingSubcommand
from smorgasDB import BaseAddition, Guild


class Hearer(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.reset_database_on_start = True

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This method is called Smorg is connected to Discord.
        It assures that it has stored Guild information for every Guild that it is a part of.
        This is important because it must know in which channel it should perform some of its functions.
        :return: None.
        """
        if self.reset_database_on_start:
            BaseAddition.reset_database()
        for guild in self.bot.guilds:
            if Guild.exists_with(guild.id):
                channel_id: int = Guild.get_reminder_channel_by(guild.id)
                ready_channel: discord.TextChannel = self.bot.get_channel(channel_id)
            else:
                general_channels = [channel for channel in guild.text_channels if channel.name == 'general']
                if general_channels:
                    default_channel_id: int = general_channels[0].id
                elif len(guild.text_channels) > 0:
                    default_channel_id = guild.text_channels[0].id
                else:
                    raise ...  # TODO raise actual error: no text channels
                Guild.create_guild_with(guild.id, default_channel_id)
                ready_channel = self.bot.get_channel(default_channel_id)
            # await ready_channel.send(
            #    "Hello! Smorg is online! To view commands, please use the 'help' command with the appropriate prefix. "
            #    "If this is your first time using this bot, '.' is your prefix."
            # )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if not isinstance(error, commands.CommandNotFound):
            command_name: str = ctx.command.name.title()
            if isinstance(error, commands.UserInputError):
                if isinstance(error, MissingSubcommand):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Missing Subcommand',
                        description=f'You did not supply a subcommand '
                                    f'{error.subcommand_depth} level{"s" if error.subcommand_depth > 1 else ""} deep.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.MissingRequiredArgument):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Missing Required Argument',
                        description='You supplied too few arguments to this command.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.TooManyArguments):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Too Many Arguments',
                        description='You supplied too many arguments to this command.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.BadArgument):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Bad Argument',
                        description='One of your arguments (likely a Discord-related item) is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.BadUnionArgument):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Bad Argument',
                        description=f'The argument {error.param} could not be converted to a valid value '
                                    f'for one of this command\'s arguments.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.UnexpectedQuoteError):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Unexpected Quotation Mark',
                        description='You added an unexpected quotation mark that inhibits parsing.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Post-Quotation Character',
                        description='You added an unexpected character after a quotation mark that inhibits parsing.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.ExpectedClosingQuoteError):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Unfinished Quotation Mark',
                        description='You forgot a closing quotation mark.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, commands.ArgumentParsingError):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Argument Parsing Error',
                        description='You supplied an argument that could not be parsed.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, InvalidDay):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Day',
                        description=f'The given day is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, InvalidHour):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Hour',
                        description=f'The given hour is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, InvalidMinute):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Minute',
                        description=f'The given minute is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, InvalidMonth):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Month',
                        description=f'The given month is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, InvalidTimeZone):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Time Zone',
                        description=f'The given time zone is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                elif isinstance(error, InvalidYear):
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): Invalid Year',
                        description=f'The given year is invalid.',
                        color=ColorConstant.ERROR_RED
                    )
                else:
                    error_embed = discord.Embed(
                        title=f'Error ({command_name}): User Input Error',
                        description='Something about your input could not be processed.',
                        color=ColorConstant.ERROR_RED
                    )
            elif isinstance(error, commands.ConversionError):
                error_embed = discord.Embed(
                    title=f'Error ({command_name}): Conversion Error',
                    description="There was an invalid conversion in processing your command.",
                    color=ColorConstant.ERROR_RED
                )
            else:
                error_embed = discord.Embed(
                    title=f'Error ({command_name}): Miscellaneous Error',
                    description=f'The error type is: {error}. A better error message will be supplied soon.',
                    color=ColorConstant.ERROR_RED
                )
            await ctx.send(embed=error_embed)
