# TODO: documentation
# TODO: is there any way to automate how I retrieve the errors in passable_errors beyond commands.CommandNotFound?
# TODO: moreover, I'm not sure about the behavior for errors that aren't my own or CommandNotFound.
# Is there a way to make it so they only are passed when I do, in fact, handle them previously?


from discord import Embed, TextChannel
from discord.ext import commands
from sqlalchemy.exc import DataError

from Cogs.Helpers.exceptioner import *
from smorgasDB import BaseAddition, Guild


class Hearer(commands.Cog, Exceptioner):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.passable_errors: tuple = (
            commands.CommandNotFound, DataError,
            DuplicateOperator, ImproperFunction, MissingParenthesis, InvalidRecipient,
            MissingReminder, InvalidRoll, InvalidSequence
        )
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
                ready_channel: TextChannel = self.bot.get_channel(channel_id)
            else:
                general_channels = [channel for channel in guild.text_channels if channel.name == 'general']
                if general_channels:
                    default_channel_id: int = general_channels[0].id
                elif len(guild.text_channels) > 0:
                    default_channel_id = guild.text_channels[0].id
                else:
                    raise ...  # TODO raise actual error: no text channels
                Guild.create_guild_with(guild.id, default_channel_id)
                # ready_channel = self.bot.get_channel(default_channel_id)
            # await ready_channel.send(
            #    "Hello! Smorg is online! To view commands, please use the 'help' command with the appropriate prefix. "
            #    "If this is your first time using this bot, '.' is your prefix."
            # )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if not isinstance(error, self.passable_errors) and (isinstance(error, commands.CommandInvokeError) and
                                                            not isinstance(error.original, self.passable_errors)):
            command_name: str = ctx.command.name.title()
            error_name: str = await self.compose_error_name(error.__class__.__name__)
            if isinstance(error, commands.UserInputError):
                if isinstance(error, MissingSubcommand):
                    error_description: str = f'You did not supply a subcommand {error.subcommand_depth} ' \
                                             f'level{"s" if error.subcommand_depth > 1 else ""} deep.'
                elif isinstance(error, commands.MissingRequiredArgument):
                    error_description = 'You supplied too few arguments to this command.'
                elif isinstance(error, commands.TooManyArguments):
                    error_description = 'You supplied too many arguments to this command.'
                elif isinstance(error, commands.BadArgument):
                    error_description = 'One of your arguments (likely a Discord-related item) is invalid.'
                elif isinstance(error, commands.BadUnionArgument):
                    error_description = f'The argument {error.param} could not be converted to a valid value ' \
                                        f'for one of this command\'s arguments.'
                elif isinstance(error, commands.UnexpectedQuoteError):
                    error_description = 'You added an unexpected quotation mark that inhibits parsing.'
                elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                    error_description = 'You added an unexpected character after a quotation mark ' \
                                        'that inhibits parsing.'
                elif isinstance(error, commands.ExpectedClosingQuoteError):
                    error_description = 'You forgot a closing quotation mark.'
                elif isinstance(error, commands.ArgumentParsingError):
                    error_description = 'You supplied an argument that could not be parsed.'
                elif isinstance(error, InvalidDay):
                    error_description = 'The given day is invalid.'
                elif isinstance(error, InvalidHour):
                    error_description = 'The given hour is invalid.'
                elif isinstance(error, InvalidMinute):
                    error_description = 'The given minute is invalid.'
                elif isinstance(error, InvalidMonth):
                    error_description = 'The given month is invalid.'
                elif isinstance(error, InvalidTimeZone):
                    error_description = 'The given time zone is invalid.'
                elif isinstance(error, InvalidYear):
                    error_description = 'The given year is invalid.'
                else:
                    error_description = 'Something about your input could not be processed.'
            elif isinstance(error, commands.ConversionError):
                error_description = 'There was an invalid conversion in processing your command.'
            else:
                error_name = 'Miscellaneous Error'
                error_description = f'The error type is: {error}. A better error message will be supplied soon.'
            error_embed: Embed = await self.initialize_error_embed(command_name, error_name, error_description)
            await ctx.send(embed=error_embed)
