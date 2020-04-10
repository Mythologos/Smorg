# TODO: documentation

import datetime
import discord
from discord.ext import commands
from typing import Optional

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.embedder import Embedder
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone, InvalidYear
from Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from smorgasDB import Guild


class Helper(Chronologist, commands.Cog, Embedder):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command(name='help', description=HelpDescription.SUPPORT)
    async def support(self, ctx: commands.Context):
        """
        This method displays Smorg's help menu.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        sorted_commands = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        embed_items: dict = {
            "items": "commands",
            "color": ColorConstant.VIBRANT_PURPLE,
        }
        field_items: dict = {
            "current_prefix": ctx.prefix
        }
        await self.embed(ctx, sorted_commands, initialize_embed=self.initialize_itemized_embed,
                         initialize_field=self.initialize_support_field,
                         embed_items=embed_items, field_items=field_items)

    @staticmethod
    async def initialize_support_field(command: commands.Command, current_prefix: str):
        name: str = f"{current_prefix}{command.name}"
        description: str = f"{current_prefix}{command.description}"
        inline: bool = False
        return name, description, inline

    @commands.command(description=HelpDescription.OBSERVE)
    async def observe(self, ctx: commands.Context, new_prefix: str) -> None:
        Guild.update_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"You've updated your Guild's prefix to '{new_prefix}'.")

    @observe.error
    async def observe_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Observe): Missing Prefix',
                description='You didn\'t supply a prefix.',
                color=ColorConstant.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Observe): Unfinished Quotation',
                description='You forgot a closing quotation mark on your prefix.',
                color=ColorConstant.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Observe)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstant.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    @commands.command(description=HelpDescription.PURGE)
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
                color=ColorConstant.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Purge): Unfinished Quotation',
                description='You forgot a closing quotation mark on one of your times.',
                color=ColorConstant.ERROR_RED
            )
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, InvalidDay):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Day',
                    description=f'The given day is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            elif isinstance(error, InvalidHour):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Hour',
                    description=f'The given hour is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            elif isinstance(error, InvalidMinute):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Minute',
                    description=f'The given minute is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            elif isinstance(error, InvalidMonth):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Month',
                    description=f'The given month is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            elif isinstance(error, InvalidTimeZone):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Time Zone',
                    description=f'The given time zone is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            elif isinstance(error, InvalidYear):
                error_embed = discord.Embed(
                    title='Error (Purge): Invalid Year',
                    description=f'The given year is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            elif isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Purge): Missing Required Argument',
                    description=f'The given time zone is invalid.',
                    color=ColorConstant.ERROR_RED
                )
            else:
                error_embed = discord.Embed(
                    title='Error (Remind): User Input Error',
                    description=f'The error type is: {error}. A better error message will be supplied soon.',
                    color=ColorConstant.ERROR_RED
                )
        else:
            error_embed = discord.Embed(
                title='Error (Purge)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstant.ERROR_RED
            )
        await ctx.send(embed=error_embed)
