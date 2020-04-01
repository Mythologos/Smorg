# GMT: https://greenwichmeantime.com/time-zone/definition/
# aenum: https://bitbucket.org/stoneleaf/aenum/src/default/aenum/doc/aenum.rst
# TODO: be sure to add Disambiguator TimeoutError handling

import discord
import datetime
import re
from discord.ext import commands
from typing import Union

from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator
from Cogs.Helpers.Enumerators.timekeeper import HourConstants, MonthConstants, PeriodConstants, TimeZone
from Cogs.Helpers.Enumerators.universalist import ColorConstants, HelpDescriptions


class Recaller(commands.Cog, Disambiguator):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.time_zones: list = []
        for i in range(TimeZone.get_lowest_zone_value(), TimeZone.get_highest_zone_value() + 1):
            self.time_zones.append(TimeZone(i))
        self.twelve_hour_periods: tuple = ('a.m.', 'am', 'p.m.', 'pm')

    # TODO: documentation...
    @commands.command(description=HelpDescriptions.REMIND)
    async def remind(self, ctx: commands.Context, mentionable: Union[discord.Member, discord.Role],
                     reminder_time: str, message: str = "") -> None:
        reminder_response = "Your reminder has been successfully processed! It'll be sent at the specified time."
        await self.handle_time(mentionable, reminder_time, message)
        current_guild = ctx.guild
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild.id)
        current_channel = self.bot.get_channel(reminder_channel_id)
        await current_channel.send(reminder_response)

    @commands.command(description=HelpDescriptions.REVISE)
    async def revise(self, ctx: commands.Context, name: Union[discord.Member, discord.Role], old_reminder_time: str,
                     new_reminder_time: str, new_message: str = ""):
        raise NotImplementedError

    # TODO: documentation... "forgets" a reminder
    @commands.command(description=HelpDescriptions.FORGET)
    async def forget(self, ctx: commands.Context, name: Union[discord.Member, discord.Role], reminder_time: str):
        raise NotImplementedError

    # TODO: documentation... lists server reminder
    # do I want this command name? is this the best command name?
    # @commands.command(description=HelpDescriptions.TIMETABLE)
    # async def timetable(self, ctx: commands.Context):
        # raise NotImplementedError

    async def handle_time(self, mentionable: Union[discord.Member, discord.Role], reminder_time: str,
                          message: str) -> None:
        parsed_time = await self.parse_time(reminder_time)
        validated_time: dict = await self.validate_time(parsed_time)

    @staticmethod
    async def parse_time(reminder_time: str):
        datetime_pattern = re.compile(
            r'(?:(?P<time>'
            r'(?P<hour>[012][\d])(?:[:]'
            r'(?P<minute>[012345][\d])(?:[\s](?P<period>(?:(?P<post>[pP])|(?P<ante>[aA]))[.]?[mM][.]?))?)?)'
            r'(?:[\s](?P<time_zone>[\dA-Z+\-]{3,6}))?'
            r'(?:[;][\s](?P<date>(?P<day>[0123]?[\d])'
            r'(?:[\s](?P<month>Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|'
            r'Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|[01][\d])'
            r'(?:[\s](?P<year>[\d]{0,4}))?)?))?)'
        )
        return re.match(datetime_pattern, reminder_time)

    # Notes:
    # The above reads the time as a requirement. Can be in 24-hour or 12-hour time;
    # the period modifier determines which. Period can be ante- or post-meridiem with or without dots.
    # Dates are not required. If included, days are required first, then months, then years.
    # If sequential items are not included, the current or nearest item is assumed.
    # e.g. day = today or tomorrow depending on the time;
    # month = next month in which the day occurs;
    # year = next year in which the month occurs.
    # Validation is required for most items to assure that they have not occurred yet and are legal values.
    # Months, if in English text, must be converted (just by an if/elif chain or dict) to their numerical values.
    # Time zone defaults to the one that the DB will hold for a Guild;
    # if specified, it'll be determined using timekeeper and disambiguated with disambiguator if need be.
    # Minutes are not required. The default is on the hour (AKA 0 minutes)

    async def validate_time(self, reminder_time) -> dict:
        period = await self.validate_period(reminder_time.group('post_value'), reminder_time.group('ante_value'))
        time_zone = await self.validate_time_zone(reminder_time.group('time_zone'))
        month = await self.validate_month(reminder_time.group('month'))
        year = await self.validate_year(reminder_time.group('year'))
        return {
            'hours': await self.validate_hour(reminder_time.group('hour'), period, time_zone),
            'minutes': await self.validate_minute(reminder_time.group('minute')),
            'period': period,
            'time_zone': time_zone,
            'day': await self.validate_day(reminder_time.group('day'), month, year),
            'month': month,
            'year': year
        }

    @staticmethod
    async def validate_hour(hour_value: str, period, time_zone):
        ...
        return ...

    @staticmethod
    async def validate_minute(minute_value: str) -> int:
        if not minute_value:
            minute: int = 0
        elif HourConstants.START_MINUTE <= int(minute_value) <= HourConstants.END_MINUTE:
            minute = int(minute_value)
        else:
            raise NotImplementedError  # TODO: give better error
        return minute

    @staticmethod
    async def validate_period(post_value: str, ante_value: str) -> int:
        if not (post_value and ante_value):
            period = PeriodConstants.SINE_MERIDIEM
        elif ante_value:
            period = PeriodConstants.ANTE_MERIDIEM
        else:
            period = PeriodConstants.POST_MERIDIEM
        return period

    @staticmethod
    async def validate_time_zone(time_zone_value: str):
        ...
        return ...

    @staticmethod
    async def validate_day(day_value: str, month, year):
        ...
        return ...

    @staticmethod
    async def validate_month(month_value: str):
        if not month_value:
            month: int = datetime.date.today().month
        elif month_value in MonthConstants.JANUARY:
            month: int = 1
        elif month_value in MonthConstants.FEBRUARY:
            month = 2
        elif month_value in MonthConstants.MARCH:
            month = 3
        elif month_value in MonthConstants.APRIL:
            month = 4
        elif month_value in MonthConstants.MAY:
            month = 5
        elif month_value in MonthConstants.JUNE:
            month = 6
        elif month_value in MonthConstants.JULY:
            month = 7
        elif month_value in MonthConstants.AUGUST:
            month = 8
        elif month_value in MonthConstants.SEPTEMBER:
            month = 9
        elif month_value in MonthConstants.OCTOBER:
            month = 10
        elif month_value in MonthConstants.NOVEMBER:
            month = 11
        elif month_value in MonthConstants.DECEMBER:
            month = 12
        else:
            raise NotImplementedError  # TODO: some better error here
        return month

    @staticmethod
    async def validate_year(year_value: str):
        current_year = datetime.date.today().year
        if not year_value:
            year: int = current_year
        elif current_year >= int(year_value):
            year = int(year_value)
        else:
            raise NotImplementedError  # TODO: some better error here
        return year

    # TODO: take from the following what I want and likely trash most of it.
    async def select_time(self, ctx: commands.Context, reminder_time):
        datetime_components = reminder_time.split(',')
        try:
            full_time: list = datetime_components[0].split(' ')
            numerical_time: list = full_time[0].split(':')
            hours: int = int(numerical_time[0])
            minutes: int = int(numerical_time[1])
        except ValueError:
            invalid_time_embed = discord.Embed(title='Error (Remind): Invalid Time Formatting',
                                               description='You didn\'t give a time with correctly-formatted, ' +
                                                           'numerical hours and minutes.',
                                               color=ColorConstants.ERROR_RED)
            await ctx.send(embed=invalid_time_embed)
        else:
            if len(full_time) > 1:
                if len(full_time) > 2:
                    try:
                        period: str = full_time[1].lower()
                        time_zone: str = full_time[2].lower()
                        assert (period in self.twelve_hour_periods and
                                time_zone in self.get_time_zone_aliases()), \
                            'Time period and time zone must be recognizable to the program.'
                    except AssertionError:
                        invalid_time_format_embed = discord.Embed(title='Error (Remind): Invalid Time Formatting',
                                                                  description='You didn\'t give a time with ' +
                                                                              'a valid time zone or time period.',
                                                                  color=ColorConstants.ERROR_RED)
                        await ctx.send(embed=invalid_time_format_embed)
                    else:
                        hours, minutes = await self.convert_to_military_time(ctx, hours, minutes, period)
                        hours, minutes = await self.convert_to_standard_time(ctx, hours, minutes, time_zone)
                elif reminder_time[1] in self.twelve_hour_periods:
                    period: str = full_time[1].lower()
                    hours, minutes = self.convert_to_military_time(ctx, hours, minutes, period)
                elif reminder_time[1] in self.time_zones:
                    time_zone: str = full_time[1].lower()
                    hours, minutes = self.convert_to_standard_time(ctx, hours, minutes, time_zone)
                else:
                    ...
                    # TODO: handle time formatting.
                    # TIME: "12:00 [P.M.] [EST]"
                    # DATE: "4 January 2019"
                # TODO: handle dates
            return hours, minutes

    @staticmethod
    async def convert_to_military_time(ctx: commands.Context, hours: int, minutes: int, period: str) -> tuple:
        try:
            assert (0 < hours <= 12 and 0 <= minutes <= 59), 'Function only accepts valid twelve-hour times.'
        except AssertionError:
            invalid_time_embed = discord.Embed(title='Error (Remind): Invalid Time',
                                               description='You didn\'t give a valid numerical time.',
                                               color=ColorConstants.ERROR_RED)
            await ctx.send(embed=invalid_time_embed)
        else:
            if period in ['pm', 'p.m'] and hours != 12:
                hours += 12
            elif period in ['am', 'a.m.'] and hours == 12:
                hours = 0
            return hours, minutes

    # converts time zone to a standard.
    # TODO: instead of GMT +/- 0, convert to database time zone?
    async def convert_to_standard_time(self, ctx: commands.Context, hours: int, minutes: int, time_zone):
        retrieved_time_zones: list = self.get_time_zones_by_alias(time_zone)
        chosen_time_zone_index: int = await Disambiguator.disambiguate(self.bot, ctx, retrieved_time_zones)
        time_zone_number = retrieved_time_zones[chosen_time_zone_index].value
        while time_zone_number != 0:
            if time_zone_number > 0:
                hours -= 1
                time_zone_number -= 1
            else:
                hours += 1
                time_zone_number += 1
        return hours, minutes

    def get_time_zone_aliases(self):
        time_zone_aliases = set(alias for gmt_zone in self.time_zones for alias in gmt_zone.aliases)
        return time_zone_aliases

    def get_time_zones_by_alias(self, given_alias):
        selected_time_zones: list = [gmt_zone for gmt_zone in self.time_zones if given_alias in gmt_zone]
        return selected_time_zones
