# TODO: be sure to add Disambiguator TimeoutError handling

import discord
import datetime

from discord.ext import commands
from typing import Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone, InvalidYear
from Cogs.Helpers.Enumerators.universalist import ColorConstants, HelpDescriptions
from smorgasDB import Guild, Reminder


class Recaller(commands.Cog, Chronologist):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()

    # TODO: documentation...
    @commands.command(description=HelpDescriptions.REMIND)
    async def remind(self, ctx: commands.Context, mentionable: Union[discord.Member, discord.Role],
                     reminder_time: str, message: str = "") -> None:
        reminder_response = "Your reminder has been successfully processed! It'll be sent at the specified time."
        current_guild_id = ctx.guild.id
        await self.handle_time(current_guild_id, mentionable.mention, reminder_time, message)
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild_id)
        current_channel = self.bot.get_channel(reminder_channel_id)
        await current_channel.send(reminder_response)

    # TODO: documentation ... "revises" a reminder
    @commands.command(description=HelpDescriptions.REVISE)
    async def revise(self, ctx: commands.Context, name: Union[discord.Member, discord.Role], old_reminder_time: str,
                     new_reminder_time: str, new_message: str = ""):
        raise NotImplementedError

    # TODO: documentation... "forgets" a reminder
    @commands.command(description=HelpDescriptions.FORGET)
    async def forget(self, ctx: commands.Context, name: Union[discord.Member, discord.Role], reminder_time: str):
        raise NotImplementedError

    async def handle_time(self, guild_id: int, mentionable: Union[discord.Member, discord.Role],
                          reminder_time: str, message: str) -> None:
        default_tz: datetime.timezone = datetime.timezone.utc
        today: datetime.datetime = datetime.datetime.now(default_tz)
        additional_validators: tuple = (self.validate_future_datetime,)
        temporal_defaults: dict = {
            "default_hour": None, "default_minute": 0, "default_tz": default_tz, "default_day": today.day,
            "default_month": today.month, "default_year": today.year
        }
        validated_datetime: datetime.datetime = await self.process_temporality(
            reminder_time, self.parse_aware_datetime, self.validate_datetime,
            additional_validators=additional_validators, temporal_defaults=temporal_defaults
        )
        Reminder.create_reminder_with(guild_id, mentionable, message, validated_datetime)

    @remind.error
    async def remind_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.UserInputError):
            if isinstance(error, InvalidDay):
                error_embed = discord.Embed(
                    title='Error (Remind): Invalid Day',
                    description=f'The given day is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidHour):
                error_embed = discord.Embed(
                    title='Error (Remind): Invalid Hour',
                    description=f'The given hour is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidMinute):
                error_embed = discord.Embed(
                    title='Error (Remind): Invalid Minute',
                    description=f'The given minute is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidMonth):
                error_embed = discord.Embed(
                    title='Error (Remind): Invalid Month',
                    description=f'The given month is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidTimeZone):
                error_embed = discord.Embed(
                    title='Error (Remind): Invalid Time Zone',
                    description=f'The given time zone is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidYear):
                error_embed = discord.Embed(
                    title='Error (Remind): Invalid Year',
                    description=f'The given year is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Remind): Missing Required Argument',
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
                title='Error (Remind): Miscellaneous Error',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)
