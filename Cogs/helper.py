# TODO: documentation

import datetime
import discord
from discord.ext import commands
from typing import Optional

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone, InvalidYear
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions
from smorgasDB import Guild


class Helper(Chronologist, commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command(name='help', description=HelpDescriptions.SUPPORT)
    async def support(self, ctx: commands.Context):
        """
        This method displays Smorg's help menu.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        support_embed = discord.Embed(
            title='Smorg Support, Page 1',
            description='This bot supports the following commands:',
            color=ColorConstants.VIBRANT_PURPLE
        )
        sorted_commands = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        for counter, command in enumerate(sorted_commands):
            if counter and (counter % DiscordConstants.MAX_EMBED_FIELDS) == 0:
                await ctx.send(embed=support_embed)
                support_embed = discord.Embed(
                    title=f'Smorg Support, Page {(counter // DiscordConstants.MAX_EMBED_FIELDS) + 1}',
                    description='This bot also supports these commands:',
                    color=ColorConstants.VIBRANT_PURPLE
                )
            support_embed.add_field(
                name=f".{command.name}",
                value=command.description,
                inline=False
            )
        await ctx.send(embed=support_embed)

    @commands.command(description=HelpDescriptions.OBSERVE)
    async def observe(self, ctx: commands.Context, new_prefix: str) -> None:
        Guild.update_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"You've updated your Guild's prefix to '{new_prefix}'.")

    @observe.error
    async def observe_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Observe): Missing Prefix',
                description='You didn\'t supply a prefix.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Observe): Unfinished Quotation',
                description='You forgot a closing quotation mark on your prefix.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Observe)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    @commands.command(description=HelpDescriptions.PURGE)
    async def purge(self, ctx: commands.Context, message_count: Optional[int], from_time: Optional[str],
                    to_time: Optional[str]):
        today: datetime.datetime = datetime.datetime.today()
        additional_validators: tuple = (self.validate_past_datetime,)
        datetime_defaults: dict = {'default_minute': None, 'default_hour': None, 'default_day': today.day,
                                   'default_month': today.month, 'default_year': today.year,
                                   'default_tz': None}
        start_time: datetime.datetime = await self.process_temporality(
            from_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators, temporal_defaults=datetime_defaults
        ) if from_time else None

        end_time: datetime.datetime = await self.process_temporality(
            to_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators, temporal_defaults=datetime_defaults
        ) if to_time else None

        history_args: dict = {}
        if start_time:
            start_time = await self.convert_to_naive_timezone(start_time)
            history_args["after"] = start_time
        if end_time:
            end_time = await self.convert_to_naive_timezone(end_time)
            history_args["before"] = end_time
        if message_count:
            history_args["limit"] = message_count
        elif not (start_time and end_time) and not message_count:
            message_count = 1
            history_args["limit"] = message_count

        delete_count: int = 0
        await ctx.message.delete()
        async for message in ctx.message.channel.history(**history_args):
            await message.delete()
            delete_count += 1
        else:
            await ctx.send(f"You've deleted up to {message_count or delete_count} messages just now.")

    # TODO: figure out a way to combine some of these errors into a common handler.
    # Perhaps use an dictionary?
    @purge.error
    async def purge_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Purge): Missing Required Argument',
                description='WIP',  # TODO: error message
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Purge): Unfinished Quotation',
                description='You forgot a closing quotation mark on one of your times.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, InvalidDay):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Day',
                    description=f'The given day is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidHour):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Hour',
                    description=f'The given hour is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidMinute):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Minute',
                    description=f'The given minute is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidMonth):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Month',
                    description=f'The given month is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidTimeZone):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Time Zone',
                    description=f'The given time zone is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidYear):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Year',
                    description=f'The given year is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Purge): Missing Required Argument',
                    description=f'The given time zone is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            else:
                error_embed = discord.Embed(
                    title='Error (Remind): User Input Error',
                    description=f'The error type is: {error}. A better error message will be supplied soon.',
                    color=ColorConstants.ERROR_RED
                )
        else:
            error_embed = discord.Embed(
                title='Error (Purge)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)
