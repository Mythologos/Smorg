# GMT: https://greenwichmeantime.com/time-zone/definition/
# aenum: https://bitbucket.org/stoneleaf/aenum/src/default/aenum/doc/aenum.rst
# TODO: be sure to add Disambiguator TimeoutError handling

import discord
import re
from discord.ext import commands
from typing import Union

from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator
from Cogs.Helpers.Enumerators.timekeeper import TimeZone
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
    async def remind(self, ctx: commands.Context, name: Union[discord.Member, discord.Role],
                     reminder_time: str, message: str = ""):
        reminder_response = "Your reminder has been successfully processed! " + \
                            "It will be sent at the specified time."
        current_guild = ctx.guild
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild.id)
        current_channel = self.bot.get_channel(reminder_channel_id)
        if reminder_time:
            selected_time = self.select_time(ctx, reminder_time)
        else:
            reminder_response = "Error: that time is invalid. Please try again."
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

    @staticmethod
    async def parse_time(reminder_time: str):
        datetime_pattern = re.compile(
            r'(?:(?P<time>'
            r'(?P<hours>[012][\d]):'
            r'(?P<minutes>[012345][\d])(?:[\s](?P<period>(?:(?P<post>[pP])|(?P<ante>[aA]))[.]?[mM][.]?))?)'
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
