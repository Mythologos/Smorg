# TODO: be sure to add Disambiguator TimeoutError handling

import discord
import datetime
import re
from discord.ext import commands
from typing import Optional, Union

from smorgasDB import Guild, Reminder
from Cogs.Helpers.cataloguer import Cataloguer
from Cogs.Helpers.exceptioner import InvalidDay, InvalidHour, InvalidMinute, InvalidMonth, InvalidTimeZone, InvalidYear
from Cogs.Helpers.Enumerators.timekeeper import DateConstants, MonthAliases, MonthConstants, PeriodConstants, \
    TimeConstants, TimeZone
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions


class Recaller(commands.Cog, Cataloguer):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.time_zones: list = []
        for i in range(TimeZone.get_lowest_zone_value(), TimeZone.get_highest_zone_value() + 1):
            self.time_zones.append(TimeZone(i))

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

    @commands.command(description=HelpDescriptions.REVISE)
    async def revise(self, ctx: commands.Context, name: Union[discord.Member, discord.Role], old_reminder_time: str,
                     new_reminder_time: str, new_message: str = ""):
        raise NotImplementedError

    # TODO: documentation... "forgets" a reminder
    @commands.command(description=HelpDescriptions.FORGET)
    async def forget(self, ctx: commands.Context, name: Union[discord.Member, discord.Role], reminder_time: str):
        raise NotImplementedError

    # TODO: documentation... lists server reminders
    # do I want this command name? is this the best command name?
    # @commands.command(description=HelpDescriptions.TIMETABLE)
    # async def timetable(self, ctx: commands.Context):
        # raise NotImplementedError

    async def handle_time(self, guild_id: int, mentionable: Union[discord.Member, discord.Role],
                          reminder_time: str, message: str) -> None:
        parsed_time = await self.parse_time(reminder_time)
        validated_time: dict = await self.validate_time(parsed_time)
        reminder_datetime: datetime.datetime = datetime.datetime(
            year=validated_time['year'],
            month=validated_time['month'],
            day=validated_time['day'],
            hour=validated_time['hour'],
            minute=validated_time['minute'],
            tzinfo=validated_time['time_zone']
        )
        await self.validate_complete_datetime(reminder_datetime, validated_time['time_zone'])
        Reminder.create_reminder_with(guild_id, mentionable, message, reminder_datetime)

    @staticmethod
    async def parse_time(reminder_time: str):
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

    @staticmethod
    async def validate_complete_datetime(complete_datetime: datetime.datetime, time_zone) -> None:
        today = datetime.datetime.now(time_zone)
        if complete_datetime < today:
            if complete_datetime.year < today.year:
                raise InvalidYear
            elif complete_datetime.month < today.month:
                raise InvalidMonth
            elif complete_datetime.day < today.day:
                raise InvalidDay
            elif complete_datetime.hour < today.hour:
                raise InvalidHour
            else:
                raise InvalidMinute

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

    @Cataloguer.display.command()
    async def zones(self, ctx: commands.Context) -> None:
        sorted_time_zones = sorted(self.time_zones, key=lambda tz: tz.value)
        time_zone_embed = discord.Embed(
            title="Time Zone Aliases by GMT Offset, Page 1",
            description="The time zones accepted in writing times include:",
            color=ColorConstants.NEUTRAL_ORANGE
        )
        for counter, time_zone in enumerate(sorted_time_zones):
            alias_string = ", ".join(time_zone.aliases) if time_zone.aliases else "None"
            if counter and (counter % DiscordConstants.MAX_EMBED_FIELDS) == 0:
                await ctx.send(embed=time_zone_embed)
                time_zone_embed = discord.Embed(
                    title=f'Time Zone Aliases by GMT Offset, Page {(counter // DiscordConstants.MAX_EMBED_FIELDS) + 1}',
                    description='This bot also supports these commands:',
                    color=ColorConstants.NEUTRAL_ORANGE
                )
            time_zone_embed.add_field(
                name=f"Zone {time_zone.value}",
                value=alias_string,
                inline=False
            )
        await ctx.send(embed=time_zone_embed)

    @Cataloguer.display.command()
    async def reminders(self, ctx: commands.Context,
                        mentionable: Optional[Union[discord.Member, discord.Role]] = None) -> None:
        mention = mentionable.mention if mentionable else ctx.message.author.mention
        reminder_list: list = Reminder.get_reminders_by(ctx.guild.id, mention)
        reminder_embed: discord.Embed = discord.Embed(
            name=f"The Reminders of {mentionable.name}, Page 1",
            description="The upcoming reminders related to this mentionable are:",
            color=ColorConstants.NEUTRAL_ORANGE  # TODO: maybe change color?
        )
        for counter, (reminder_datetime, reminder_message) in enumerate(reminder_list):
            if counter and counter % DiscordConstants.MAX_EMBED_FIELDS == 0:
                await ctx.send(embed=reminder_embed)
                reminder_embed: discord.Embed = discord.Embed(
                    name=f"The Reminders of {mentionable.name}, Page {(counter // 25) + 1}",
                    description="Further upcoming reminders related to this mentionable are:",
                    color=ColorConstants.NEUTRAL_ORANGE  # TODO: maybe change color?
                )
            reminder_embed.add_field(
                name=f"Reminder at {reminder_datetime.strftime(r'%H:%M UTC%Z on %d %b %Y')}",
                value=f"{reminder_message}",
                inline=False
            )
        else:
            if len(reminder_embed.fields) == 0:
                today = datetime.datetime.now(tz=datetime.timezone.utc)
                reminder_embed.add_field(
                    name=f"Note at {today.strftime(r'%H:%M %Z on %d %b %Y')}",
                    value="No reminders are available for this mentionable.",
                    inline=False
                )
        await ctx.send(embed=reminder_embed)
