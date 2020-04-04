# TODO: alter time-related functions here so that they can be used more widely, treated as mix-ins.

import re
import datetime
from typing import Union

from Cogs.Helpers.Enumerators.timekeeper import DateConstants, MonthAliases, MonthConstants, PeriodConstants,\
    TimeConstants, TimeZone
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone


class Chronologist:
    def __init__(self):
        self.time_zones: list = []
        for i in range(TimeZone.get_lowest_zone_value(), TimeZone.get_highest_zone_value() + 1):
            self.time_zones.append(TimeZone(i))

    # TODO: if this is to be more generic, do I want it to accept hour, minute, etc. in this order?
    # Do I want it to be less discriminating? How can I make this feel "generic" and "usable in different classes"?
    # Is it? Should there be separate parsers for different items (e.g. a time parser, a date parser)?
    @staticmethod
    async def parse_datetime(reminder_time: str):
        datetime_pattern = re.compile(
            r'(?:(?P<time>'
            r'(?P<hour>[012]?[\d])(?:[:]'
            r'(?P<minute>[012345][\d])(?:[\s](?P<period>(?:(?P<post>[pP])|(?P<ante>[aA]))[.]?[mM][.]?))?)?)'
            r'(?:[\s](?P<time_zone>[\da-zA-Z+\-]{3,6}))?'
            r'(?:[;][\s](?P<date>(?P<day>[0123]?[\d])'
            r'(?:[\s](?P<month>Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|'
            r'Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|[01][\d])'
            r'(?:[\s](?P<year>[\d]{0,4})?))?))?)'
        )
        return re.match(datetime_pattern, reminder_time)

    # Notes (from Recaller, may not continue to hold true now or in the future):
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

    async def validate_datetime(self, reminder_time) -> dict:
        period: int = await self.validate_period(reminder_time.group('post'), reminder_time.group('ante'))
        month: int = await self.validate_month(reminder_time.group('month'))
        year: int = await self.validate_year(reminder_time.group('year'))
        return {
            'hour': await self.validate_hour(reminder_time.group('hour'), period),
            'minute': await self.validate_minute(reminder_time.group('minute')),
            'time_zone': await self.validate_time_zone(reminder_time.group('time_zone')),
            'day': await self.validate_day(reminder_time.group('day'), month, year),
            'month': month,
            'year': year
        }

    async def validate_hour(self, hour_value: str, period: int):
        if TimeConstants.START_HOUR <= int(hour_value) <= TimeConstants.END_HOUR:
            hour = int(hour_value)
            if period:
                hour = await self.convert_to_24_hour_time(hour, period)
        else:
            raise InvalidHour
        return hour

    @staticmethod
    async def validate_minute(minute_value: str) -> int:
        if not minute_value:
            minute: int = 0
        elif TimeConstants.START_MINUTE <= int(minute_value) <= TimeConstants.END_MINUTE:
            minute = int(minute_value)
        else:
            raise InvalidMinute
        return minute

    @staticmethod
    async def validate_period(post_value: str, ante_value: str) -> int:
        if not (post_value or ante_value):
            period = PeriodConstants.SINE_MERIDIEM
        elif ante_value:
            period = PeriodConstants.ANTE_MERIDIEM
        else:
            period = PeriodConstants.POST_MERIDIEM
        return period

    async def validate_time_zone(self, time_zone_value: str) -> datetime.timezone:
        if not time_zone_value:
            # TODO: unsure of what to choose for default...
            time_delta: datetime.timedelta = datetime.timedelta(0)
            time_zone: datetime.timezone = datetime.timezone(time_delta, name="UTC")
        else:
            matching_time_zone: Union[TimeZone, None] = await self.get_time_zone_by_alias(time_zone_value)
            if matching_time_zone:
                time_delta = datetime.timedelta(hours=matching_time_zone.value)
                time_zone = datetime.timezone(time_delta, name=time_zone_value)
            else:
                raise InvalidTimeZone
        return time_zone

    @staticmethod
    async def validate_day(day_value: str, month, year) -> int:
        if not day_value:
            day: int = datetime.date.today().day
        else:
            if year % 4 and month == MonthConstants.FEBRUARY.value:
                this_month: MonthConstants = MonthConstants(13)
            else:
                this_month = MonthConstants(month)

            if DateConstants.FIRST_DAY_OF_MONTH <= int(day_value) <= this_month.number_of_days:
                day = int(day_value)
            else:
                raise InvalidDay
        return day

    @staticmethod
    async def validate_month(month_value: str) -> int:
        if not month_value:
            month: int = datetime.date.today().month
        elif month_value in MonthAliases.JANUARY:
            month: int = 1
        elif month_value in MonthAliases.FEBRUARY:
            month = 2
        elif month_value in MonthAliases.MARCH:
            month = 3
        elif month_value in MonthAliases.APRIL:
            month = 4
        elif month_value in MonthAliases.MAY:
            month = 5
        elif month_value in MonthAliases.JUNE:
            month = 6
        elif month_value in MonthAliases.JULY:
            month = 7
        elif month_value in MonthAliases.AUGUST:
            month = 8
        elif month_value in MonthAliases.SEPTEMBER:
            month = 9
        elif month_value in MonthAliases.OCTOBER:
            month = 10
        elif month_value in MonthAliases.NOVEMBER:
            month = 11
        elif month_value in MonthAliases.DECEMBER:
            month = 12
        else:
            raise InvalidMonth
        return month

    @staticmethod
    async def validate_year(year_value: str):
        current_year = datetime.date.today().year
        if not year_value:
            year: int = current_year
        else:
            year = int(year_value)
        return year

    @staticmethod
    async def convert_to_24_hour_time(hour: int, period: int) -> int:
        if TimeConstants.START_MERIDIEM_HOUR <= hour <= TimeConstants.END_MERIDIEM_HOUR:
            if period == PeriodConstants.ANTE_MERIDIEM:
                if hour == TimeConstants.END_MERIDIEM_HOUR:
                    hour -= 12
            else:
                if hour != TimeConstants.END_MERIDIEM_HOUR:
                    hour += 12
        else:
            raise InvalidHour
        return hour

    async def get_time_zone_by_alias(self, given_alias):
        selected_time_zone: Union[TimeZone, None] = None
        for zone in self.time_zones:
            if given_alias in zone.aliases:
                selected_time_zone = zone
                break
        return selected_time_zone
