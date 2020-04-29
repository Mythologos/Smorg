"""
This module contains the Chronologist mix-in, which handles the processing of dates and times
from strings to datetime, date, or time objects.
"""

import re
import datetime
from typing import Callable, Pattern, Tuple, Union

from Cogs.Helpers.Enumerators.timekeeper import DateConstant, MonthAliases, MonthConstant, PeriodConstant,\
    TimeConstant, TimeZone
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone, InvalidYear


class Chronologist:
    """
    This class contains many methods that help to parse, convert, and verify strings of dates, times, and datetimes.
    The process_temporality function is the main method which is called to handle this process,
    allowing the caller to designate the parser and validators required for the process alongside any other
    additional information.
    """
    def __init__(self):
        self.time_zones: list = TimeZone.list_time_zones()

    @staticmethod
    async def parse_datetime(datetime_string: str) -> dict:
        """
        This method parses a string into various datetime groups.
        It should be of the format: "HH:MM PP TZ; DD MONTH YY", ordered as such in accordance with
        the granularity of the data. Unlike other groups, months can be names, abbreviations, or integers.

        :param str datetime_string: a string presumably containing a date and time that meet the pattern
        given above and represented below.
        :return dict: a dictionary that correlates individual match groups to their corresponding parsed substrings.
        """
        datetime_pattern: Pattern = re.compile(
            r'(?:(?P<time>'
            r'(?P<hour>[012]?[\d])(?:[:]'
            r'(?P<minute>[012345][\d])(?:[\s](?P<period>(?:(?P<post>[pP])|(?P<ante>[aA]))[.]?[mM][.]?))?)?)'
            r'(?:[\s](?P<time_zone>[\da-zA-Z+\-]{3,6}))?'
            r'(?:[;][\s](?P<date>(?P<day>[0123]?[\d])'
            r'(?:[\s](?P<month>Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|'
            r'Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|[01][\d])'
            r'(?:[\s](?P<year>[\d]{0,4})?))?))?)'
        )
        return re.match(datetime_pattern, datetime_string).groupdict()

    @staticmethod
    async def parse_date(date_string: str) -> dict:
        """
        This method parses a string into various date groups.
        It should be of the format: "DD MONTH YY", ordered as such in accordance with
        the granularity of the data. Unlike other groups, months can be names, abbreviations, or integers.

        :param str date_string: a string presumably containing a date that meets the pattern given above and
        represented below.
        :return dict: a dictionary that correlates individual match groups to their corresponding parsed substrings.
        """
        date_pattern: Pattern = re.compile(
            r'(?P<date>(?P<day>[0123]?[\d])'
            r'(?:[\s](?P<month>Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|'
            r'Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|[01][\d])'
            r'(?:[\s](?P<year>[\d]{0,4})?))?)'
        )
        return re.match(date_pattern, date_string).groupdict()

    @staticmethod
    async def parse_time(time_string: str) -> dict:
        """
        This method parses a string into various datetime groups.
        It should be of the format: "HH:MM PP TZ", ordered as such in accordance with the granularity of the data.

        :param str time_string: a string presumably containing a time that meet the pattern given above and
        represented below.
        :return dict: a dictionary that correlates individual match groups to their corresponding parsed substrings.
        """
        time_pattern: Pattern = re.compile(
            r'(?:(?P<time>(?P<hour>[012]?[\d])'
            r'(?:[:](?P<minute>[012345][\d])'
            r'(?:[\s](?P<period>(?:(?P<post>[pP])|(?P<ante>[aA]))[.]?[mM][.]?))?)?)'
            r'(?:[\s](?P<time_zone>[\da-zA-Z+\-]{3,6}))?)'
        )
        return re.match(time_pattern, time_string).groupdict()

    async def validate_datetime(self, parsed_datetime: dict, time_zone: datetime.timezone,
                                default_hour: Union[int, None], default_minute: Union[int, None],
                                default_day: Union[int, None], default_month: Union[int, None],
                                default_year: Union[int, None]) -> datetime.datetime:
        """
        This method validates each part of a datetime object (minus the time zone, which is necessarily
        validated earlier) or makes it its default value, should that default value exist.
        It returns a complete datetime object made from all of these components.
        Some of these components are used to assure that other components are valid.

        :param dict parsed_datetime: a mapping of strings to parsed strings from a raw datetime string
        in accordance with the groups of parse_datetime().
        :param datetime.timezone time_zone: the time zone at which the given datetime is.
        :param Union[int, None] default_hour: the default hour for a given datetime, if any.
        :param Union[int, None] default_minute: the default minute for a given datetime, if any.
        :param Union[int, None] default_day: the default day for a given datetime, if any.
        :param Union[int, None] default_month: the default month for a given datetime (as an integer), if any.
        :param Union[int, None] default_year: the default year for a given datetime, if any.
        :return datetime.datetime: a legitimate datetime object with all of its components being validated.
        """
        period: int = await self.validate_period(parsed_datetime['post'], parsed_datetime['ante'])
        month: int = await self.validate_month(parsed_datetime['month'], default_month)
        year: int = await self.validate_year(parsed_datetime['year'], default_year)
        day: int = await self.validate_day(parsed_datetime['day'], month, year, default_day)
        hour: int = await self.validate_hour(parsed_datetime['hour'], period, default_hour)
        minute: int = await self.validate_minute(parsed_datetime['minute'], default_minute)
        return datetime.datetime(minute=minute, hour=hour, day=day, month=month, year=year, tzinfo=time_zone)

    async def validate_hour(self, hour_value: Union[str, None], period: int, default: Union[int, None]) -> int:
        """
        This method validates an hour, converting it from a string to an integer as necessary,
        assuring that it is valid within its time system (e.g. 24-hour time or 12-hour time) with an optional period,
        and applying a default should there be no hour_value.

        :param Union[str, None] hour_value: the value of an hour parsed from a given time string.
        :param int period: the period, if any, at which the hour is in 12-hour time.
        :param Union[int, None] default: the default value of an hour, should one be designated.
        :return int: the resultant validated value for a time's hour.
        """
        if not hour_value:
            if default is not None:
                hour: int = default
                if period:
                    hour = await self.convert_to_24_hour_time(hour, period)
            else:
                raise InvalidHour
        elif TimeConstant.START_HOUR <= int(hour_value) <= TimeConstant.END_HOUR:
            hour = int(hour_value)
            if period:
                hour = await self.convert_to_24_hour_time(hour, period)
        else:
            raise InvalidHour
        return hour

    @staticmethod
    async def validate_minute(minute_value: Union[str, None], default: Union[int, None]) -> int:
        """
        This method validates a minute, converting it from a string to an integer as necessary.

        :param Union[str, None] minute_value: the value of a minute parsed from a given time string.
        :param Union[int, None] default: the default value of a minute, should one be designated.
        :return int: the resultant validated value for a time's minute.
        """
        if not minute_value:
            if default is not None:
                minute: int = default
            else:
                raise InvalidMinute
        elif TimeConstant.START_MINUTE <= int(minute_value) <= TimeConstant.END_MINUTE:
            minute = int(minute_value)
        else:
            raise InvalidMinute
        return minute

    @staticmethod
    async def validate_period(post_value: Union[str, None], ante_value: Union[str, None]) -> int:
        """
        This method validates a period, changing it to a usable constant regardless of whether or not a period exists.

        :param Union[str, None] post_value: an indication of whether the given time is post meridiem in 12-hour time.
        :param Union[str, None] ante_value: an indication of whether the given time is ante meridiem in 12-hour time.
        :return int: the resultant validated value for a time's period.
        """
        if not (post_value or ante_value):
            period = PeriodConstant.SINE_MERIDIEM
        elif ante_value:
            period = PeriodConstant.ANTE_MERIDIEM
        else:
            period = PeriodConstant.POST_MERIDIEM
        return period

    async def validate_time_zone(self, time_zone_value: Union[str, None], default: Union[datetime.timezone, None]) \
            -> datetime.timezone:
        """
        This method validates a time zone, converting it to a time zone object should it exist.

        :param Union[str, None] time_zone_value: a string containing a time zone abbreviation, if one exists.
        :param Union[datetime.timezone, None] default: a default datetime.timezone object, should one exist.
        :return datetime.timezone: the resultant validated value for a time's timezone.
        """
        if not time_zone_value:
            time_zone: datetime.timezone = default
        else:
            matching_time_zone: Union[TimeZone, None] = await self.get_time_zone_by_alias(time_zone_value)
            if matching_time_zone:
                time_delta = datetime.timedelta(hours=matching_time_zone.value)
                time_zone = datetime.timezone(time_delta, name=time_zone_value)
            else:
                raise InvalidTimeZone
        return time_zone

    @staticmethod
    async def validate_day(day_value: Union[str, None], month: int, year: int, default: Union[int, None]) -> int:
        """
        This method validates a day, converting it from a string to an integer as necessary.

        :param Union[str, None] day_value: the value of a day parsed from a given time string.
        :param int month: the validated value of a month.
        :param int year: the validated value of a year.
        :param Union[int, None] default: the default value of a day, should one be designated.
        :return int: the resultant validated value for a date's day.
        """
        if not day_value:
            if default is not None:
                day: int = default
            else:
                raise InvalidDay
        else:
            if year % DateConstant.LEAP_YEAR_MODULO and month == MonthConstant.FEBRUARY.value:
                this_month: MonthConstant = MonthConstant(13)
            else:
                this_month = MonthConstant(month)

            if DateConstant.FIRST_DAY_OF_MONTH <= int(day_value) <= this_month.number_of_days:
                day = int(day_value)
            else:
                raise InvalidDay
        return day

    @staticmethod
    async def validate_month(month_value: Union[str, None], default: Union[int, None]) -> int:
        """
        This method validates a month, converting it from a string to an integer as necessary.

        :param Union[str, None] month_value: the value of a month parsed from a given time string.
        :param Union[int, None] default: the default value of a month, should one be designated.
        :return int: the resultant validated value for a date's month.
        """
        if not month_value:
            if default is not None:
                month: int = default
            else:
                raise InvalidMonth
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
    async def validate_year(year_value: Union[str, None], default: Union[int, None]) -> int:
        """
        This method validates a year, converting it from a string to an integer as necessary.

        :param Union[str, None] year_value: the value of a year parsed from a given time string.
        :param Union[int, None] default: the default value of a year, should one be designated.
        :return int: the resultant validated value for a date's year.
        """
        if not year_value:
            if default is not None:
                year: int = default
            else:
                raise InvalidYear
        else:
            year = int(year_value)
        return year

    @staticmethod
    async def convert_to_24_hour_time(hour: int, period: int) -> int:
        """
        This method converts an hour in 12-hour time to 24-hour time.

        :param int hour: a given hour in 12-hour time.
        :param int period: the period of the hour in 12-hour time.
        :return int: an hour in 24-hour time corresponding to its given period.
        """
        if TimeConstant.START_MERIDIEM_HOUR <= hour <= TimeConstant.END_MERIDIEM_HOUR:
            if period == PeriodConstant.ANTE_MERIDIEM:
                if hour == TimeConstant.END_MERIDIEM_HOUR:
                    hour -= 12
            else:
                if hour != TimeConstant.END_MERIDIEM_HOUR:
                    hour += 12
        else:
            raise InvalidHour
        return hour

    async def get_time_zone_by_alias(self, given_alias: str) -> TimeZone:
        """
        This method retrieves a time zone based on the alias for that time zone given as input.

        :param str given_alias: a time zone abbreviation.
        :return TimeZone: a TimeZone object corresponding to the time zone abbreviation, should one exist.
        """
        selected_time_zone: Union[TimeZone, None] = None
        for zone in self.time_zones:
            if given_alias in zone.aliases:
                selected_time_zone = zone
                break
        return selected_time_zone

    @staticmethod
    async def validate_future_datetime(valid_datetime: datetime.datetime) -> None:
        """
        This method assures that a given time zone is after the present time.

        :param datetime.datetime valid_datetime: a given validated datetime object.
        """
        today = datetime.datetime.now(valid_datetime.tzinfo) \
            if valid_datetime.tzinfo else datetime.datetime.utcnow()
        if valid_datetime < today:
            if valid_datetime.year < today.year:
                raise InvalidYear
            elif valid_datetime.month < today.month:
                raise InvalidMonth
            elif valid_datetime.day < today.day:
                raise InvalidDay
            elif valid_datetime.hour < today.hour:
                raise InvalidHour
            else:
                raise InvalidMinute

    @staticmethod
    async def validate_past_datetime(valid_datetime: datetime.datetime) -> None:
        """
        This method assures that a given time zone is before the present time.

        :param datetime.datetime valid_datetime: a given validated datetime object.
        """
        today = datetime.datetime.now(valid_datetime.tzinfo) if valid_datetime.tzinfo \
            else datetime.datetime.utcnow()
        if valid_datetime > today:
            if valid_datetime.year > today.year:
                raise InvalidYear
            elif valid_datetime.month > today.month:
                raise InvalidMonth
            elif valid_datetime.day > today.day:
                raise InvalidDay
            elif valid_datetime.hour > today.hour:
                raise InvalidHour
            else:
                raise InvalidMinute

    @staticmethod
    async def convert_to_naive_timezone(valid_datetime: datetime.datetime,
                                        time_zone: datetime.timezone = datetime.timezone.utc) -> datetime.datetime:
        """
        This method changes an aware time zone of some given time zone to a naive time zone with that aware time.
        This is advantageous for functions such as discord.py's history() that needs a naive time zone
        even though users would find it more intuitive to insert aware time zones for themselves.

        :param datetime.datetime valid_datetime: a validated datetime object.
        :param datetime.timezone time_zone: a time zone to convert the object to,
        defaulting to UTC as a universal standard time.
        :return datetime.datetime: a naive datetime with a time corresponding to the given time_zone parameter.
        """
        return valid_datetime.astimezone(time_zone).replace(tzinfo=None)

    async def generate_dt_defaults_from_tz(self, parsed_datetime: dict, manual_defaults: dict):
        """
        This method generates defaults for the creation of a datetime based on its time zone.
        This allows for defaults to be accurate regardless of the determined temporal origin of the message.

        :param dict parsed_datetime: a mapping of strings to parsed strings from a raw datetime string
        in accordance with the groups of parse_datetime().
        :param dict manual_defaults: a collection of defaults preset by the function's caller.
        :return dict: a mapping of datetime defaults based on the time zone of parsed_datetime.
        """
        validated_time_zone: datetime.timezone = await self.validate_time_zone(
            parsed_datetime['time_zone'], manual_defaults.pop("default_tz", datetime.timezone.utc)
        )
        current_datetime: datetime.datetime = datetime.datetime.now(tz=validated_time_zone)
        return {
            "time_zone": manual_defaults.pop("default_tz", current_datetime.tzinfo),
            "default_minute": manual_defaults.pop("default_minute", current_datetime.minute),
            "default_hour": manual_defaults.pop("default_hour", current_datetime.hour),
            "default_day": manual_defaults.pop("default_day", current_datetime.day),
            "default_month": manual_defaults.pop("default_month", current_datetime.month),
            "default_year": manual_defaults.pop("default_year", current_datetime.year),
        }

    @staticmethod
    async def process_temporality(temporal_string: str, temporal_parser: Callable, temporal_validator: Callable,
                                  additional_validators: Tuple[Callable], default_generator: Callable,
                                  manual_defaults: dict = None) -> \
            Union[datetime.datetime, datetime.time, datetime.date]:
        """
        This method is the overall handler for processing datetime objects. Using a designated parser,
        validator, default generator, and a collection of other validators, it fully processes a datetime object
        for use.

        :param str temporal_string: the string to be parsed and processed to produce a datetime object.
        :param Callable temporal_parser: the parser for temporal_string.
        :param Callable temporal_validator: the main validator for temporal_string.
        :param Tuple[Callable] additional_validators: additional validators for the datetime object
        drawn out of temporal_string.
        :param Callable default_generator: the function that produces default values for potentially omitted pieces
        of temporal_string.
        :param dict manual_defaults: preset defaults for the default values of temporal_string.
        :return Union[datetime.datetime, datetime.time, datetime.date]: a datetime, time, or date object
        drawn out of temporal_string and validated throughout the function.
        """
        parsed_temporality: dict = await temporal_parser(temporal_string)
        temporal_defaults: dict = await default_generator(parsed_temporality, manual_defaults)
        valid_temporality: Union[datetime.datetime, datetime.time, datetime.date] = \
            await temporal_validator(parsed_temporality, **temporal_defaults)
        for validator in additional_validators:
            await validator(valid_temporality)
        return valid_temporality
