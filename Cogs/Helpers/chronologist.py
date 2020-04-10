# TODO: maybe add checks to each validate function to assure that defaults are appropriate?

import re
import datetime
from typing import Callable, Pattern, Union

from Cogs.Helpers.Enumerators.timekeeper import DateConstants, MonthAliases, MonthConstants, PeriodConstants,\
    TimeConstants, TimeZone
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone, InvalidYear


class Chronologist:
    def __init__(self):
        self.time_zones: list = []
        for i in range(TimeZone.get_lowest_zone_value(), TimeZone.get_highest_zone_value() + 1):
            self.time_zones.append(TimeZone(i))

    @staticmethod
    async def parse_datetime(datetime_string: str) -> dict:
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

    # TODO: test the following parsing methods
    @staticmethod
    async def parse_date(date_string: str) -> dict:
        date_pattern: Pattern = re.compile(
            r'(?P<date>(?P<day>[0123]?[\d])'
            r'(?:[\s](?P<month>Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|'
            r'Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|[01][\d])'
            r'(?:[\s](?P<year>[\d]{0,4})?))?)'
        )
        return re.match(date_pattern, date_string).groupdict()

    @staticmethod
    async def parse_time(time_string: str) -> dict:
        time_pattern: Pattern = re.compile(
            r'(?:(?P<time>(?P<hour>[012]?[\d])'
            r'(?:[:](?P<minute>[012345][\d])'
            r'(?:[\s](?P<period>(?:(?P<post>[pP])|(?P<ante>[aA]))[.]?[mM][.]?))?)?)'
            r'(?:[\s](?P<time_zone>[\da-zA-Z+\-]{3,6}))?)'
        )
        return re.match(time_pattern, time_string).groupdict()

    async def validate_datetime(self, parsed_datetime: dict, default_hour: Union[int, None],
                                default_minute: Union[int, None], default_tz: Union[datetime.timezone, None],
                                default_day: Union[int, None], default_month: Union[int, None],
                                default_year: Union[int, None]) -> datetime.datetime:
        period: int = await self.validate_period(parsed_datetime['post'], parsed_datetime['ante'])
        month: int = await self.validate_month(parsed_datetime['month'], default_month)
        year: int = await self.validate_year(parsed_datetime['year'], default_year)
        day: int = await self.validate_day(parsed_datetime['day'], month, year, default_day)
        hour: int = await self.validate_hour(parsed_datetime['hour'], period, default_hour)
        minute: int = await self.validate_minute(parsed_datetime['minute'], default_minute)
        time_zone: datetime.timezone = await self.validate_time_zone(parsed_datetime['time_zone'], default_tz)
        return datetime.datetime(minute=minute, hour=hour, day=day, month=month, year=year, tzinfo=time_zone)

    async def validate_hour(self, hour_value: Union[str, None], period: int, default: Union[int, None]):
        if not hour_value:
            if default is not None:
                hour: int = default
                if period:
                    hour = await self.convert_to_24_hour_time(hour, period)
            else:
                raise InvalidHour
        elif TimeConstants.START_HOUR <= int(hour_value) <= TimeConstants.END_HOUR:
            hour = int(hour_value)
            if period:
                hour = await self.convert_to_24_hour_time(hour, period)
        else:
            raise InvalidHour
        return hour

    @staticmethod
    async def validate_minute(minute_value: Union[str, None], default: Union[int, None]) -> int:
        if not minute_value:
            if default is not None:
                minute: int = default
            else:
                raise InvalidMinute
        elif TimeConstants.START_MINUTE <= int(minute_value) <= TimeConstants.END_MINUTE:
            minute = int(minute_value)
        else:
            raise InvalidMinute
        return minute

    @staticmethod
    async def validate_period(post_value: Union[str, None], ante_value: Union[str, None]) -> int:
        if not (post_value or ante_value):
            period = PeriodConstants.SINE_MERIDIEM
        elif ante_value:
            period = PeriodConstants.ANTE_MERIDIEM
        else:
            period = PeriodConstants.POST_MERIDIEM
        return period

    async def validate_time_zone(self, time_zone_value: Union[str, None], default: Union[datetime.timezone, None]) \
            -> datetime.timezone:
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
        if not day_value:
            if default is not None:
                day: int = default
            else:
                raise InvalidDay
        else:
            if year % DateConstants.LEAP_YEAR_MODULO and month == MonthConstants.FEBRUARY.value:
                this_month: MonthConstants = MonthConstants(13)
            else:
                this_month = MonthConstants(month)

            if DateConstants.FIRST_DAY_OF_MONTH <= int(day_value) <= this_month.number_of_days:
                day = int(day_value)
            else:
                raise InvalidDay
        return day

    @staticmethod
    async def validate_month(month_value: Union[str, None], default: Union[int, None]) -> int:
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

    async def get_time_zone_by_alias(self, given_alias: str) -> TimeZone:
        selected_time_zone: Union[TimeZone, None] = None
        for zone in self.time_zones:
            if given_alias in zone.aliases:
                selected_time_zone = zone
                break
        return selected_time_zone

    # TODO: if possible, combine with validate_past_datetime
    @staticmethod
    async def validate_future_datetime(valid_datetime: datetime.datetime) -> None:
        today = datetime.datetime.now(valid_datetime.tzinfo) if valid_datetime.tzinfo \
            else datetime.datetime.utcnow()
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
        return valid_datetime.astimezone(time_zone).replace(tzinfo=None)

    @staticmethod
    async def process_temporality(temporal_string: str, temporal_parser: Callable, temporal_validator: Callable,
                                  additional_validators: tuple, temporal_defaults: dict = None) -> datetime:
        if not temporal_defaults:
            temporal_defaults = {"default_hour": None, "default_minute": None, "default_tz": None, "default_day": None,
                                 "default_month": None, "default_year": None}
        parsed_temporality: dict = await temporal_parser(temporal_string)
        valid_temporality: datetime = await temporal_validator(parsed_temporality, **temporal_defaults)
        for validator in additional_validators:
            await validator(valid_temporality)
        return valid_temporality
