"""
This module holds the hearer Cog. It is in charge of Smorg's listeners--or, at least, those that have required
a manual implementation up until this point.
"""

import discord
from discord.ext import commands

from .Helpers.exceptioner import *
from .Helpers.Enumerators.universalist import StaticText
from ..smorgasDB import BaseAddition, Guild


class Hearer(commands.Cog, Exceptioner):
    """
    This class does not center around a command; rather, it centers around the listener functions pertinent to Smorg.
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.passable_errors: tuple = (
            commands.CommandNotFound, DuplicateOperator, ImproperFunction, MissingParenthesis,
            InvalidRecipient, MissingReminder, InvalidRoll, InvalidSequence
        )
        self.reset_database_on_start = True
        self.say_hello = False

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This method fires when Smorg is starting up, performing appropriate initialization behavior.
        It is set to restart the database if one flag is ticked and also to signal to every server that it is in
        that it is ready to run.
        """
        if self.reset_database_on_start:
            BaseAddition.reset_database()
        for guild in self.bot.guilds:
            await self.signal_ready(guild)

    async def signal_ready(self, guild: discord.Guild) -> None:
        """
        This method informs each server that Smorg is online. If Smorg does not recognize a certain server,
        that server also has information about it stored in Smorg's database.

        :param discord.Guild guild: a Discord Guild of which Smorg is a member.
        """
        if Guild.exists_with(guild.id):
            channel_id: int = Guild.get_reminder_channel_by(guild.id)
            ready_channel: discord.TextChannel = self.bot.get_channel(channel_id)
            if self.say_hello:
                await ready_channel.send(StaticText.REGULAR_ON_READY_TEXT)
        elif guild.text_channels:
            general_channels: list = [channel for channel in guild.text_channels if channel.name == 'general']
            if general_channels or len(guild.text_channels) > 0:
                default_channel_id: int = general_channels[0].id
            else:
                default_channel_id = guild.text_channels[0].id
            Guild.create_guild_with(guild.id, default_channel_id)
            ready_channel = self.bot.get_channel(default_channel_id)
            if self.say_hello:
                await ready_channel.send(StaticText.NEW_ON_READY_TEXT)
        else:
            Guild.create_guild_with(guild.id, None)
            guild_owner: discord.Member = guild.owner
            if not guild_owner.dm_channel:
                await self.bot.get_user(guild_owner.id).create_dm()
            ready_channel = guild_owner.dm_channel
            if self.say_hello:
                await ready_channel.send(StaticText.ERROR_ON_READY_TEXT)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """
        This method occurs when Smorg joins a Guild. Upon joining, it signals its presence as per the signal_ready()
        method.

        :param discord.Guild guild: a Discord Guild which Smorg has just joined.
        """
        await self.signal_ready(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """
        This method occurs when Smorg leaves a Guild. Upon leaving, it deletes all information it has on that Guild.

        :param discord.Guild guild: a Discord Guild which Smorg has just left.
        """
        Guild.delete_guild_with(guild.id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        This method handles all non-Cog-exclusive Discord errors, creating and outputting a suitable Embed.

        :param commands.Context ctx: the context from which the command was made.
        :param Exception error: the error raised by some method called to fulfill a request.
        """
        error = getattr(error, "original", error)  # unwraps CommandInvoke errors
        command_name: str = getattr(ctx.command.root_parent, "name", ctx.command.name).title()
        if not isinstance(error, self.passable_errors) and isinstance(error, discord.DiscordException):
            error_name: str = await self.compose_error_name(error.__class__.__name__)
            if isinstance(error, commands.UserInputError):
                if isinstance(error, MissingSubcommand):
                    error_description: str = f'You did not supply a valid subcommand {error.subcommand_depth} ' \
                                             f'level{"s" if error.subcommand_depth > 1 else ""} deep.'
                elif isinstance(error, commands.MissingRequiredArgument):
                    error_description = 'You supplied too few arguments to this command.'
                elif isinstance(error, commands.TooManyArguments):
                    print(error)
                    error_description = 'You supplied too many arguments to this command.'
                elif isinstance(error, commands.BadArgument):
                    error_description = 'One of your arguments (likely a Discord-related item) is invalid.'
                elif isinstance(error, commands.BadUnionArgument):
                    error_description = f'The argument {error.param.name} could not be converted to a valid value ' \
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
                elif isinstance(error, InvalidComparison):
                    error_description = 'A comparison operator that was used is invalid.'
                elif isinstance(error, InvalidOperator):
                    error_description = 'An operator that was applied was invalid.'
                elif isinstance(error, InvalidFunction):
                    error_description = 'A function that was applied was invalid.'
                else:
                    error_description = 'Something about your input could not be processed.'
            elif isinstance(error, commands.CheckFailure):
                if isinstance(error, commands.BotMissingPermissions):
                    error_description = 'Smorg does not have permission to do something it wanted to do on this server.'
                elif isinstance(error, commands.MissingPermissions):
                    error_description = 'You do not have permission to perform that operation in this Guild.'
                elif ctx.command.name == 'yoink':
                    error_name = 'No Guild Quotes'
                    error_description = 'There were no quotes from which your Guild could extract a random quote.'
                else:
                    error_description = 'Smorg failed a necessary check in performing the desired operation.'
            elif isinstance(error, commands.ConversionError):
                error_description = 'There was an invalid conversion in processing your command.'
            else:
                error_name = 'Miscellaneous Error'
                error_description = f'The error type is: {error}. A better error message will be supplied soon.'
            error_embed: discord.Embed = await self.initialize_error_embed(command_name, error_name, error_description)
            await ctx.send(embed=error_embed)
