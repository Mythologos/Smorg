# GMT: https://greenwichmeantime.com/time-zone/definition/
# aenum: https://bitbucket.org/stoneleaf/aenum/src/default/aenum/doc/aenum.rst
# TODO: be sure to add Disambiguator TimeoutError handling

import discord
from discord.ext import commands

from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator
from Cogs.Helpers.Enumerators.timekeeper import TimeZone
from Cogs.Helpers.Enumerators.universalist import ColorConstants, HelpDescriptions


class Recaller(commands.Cog, Disambiguator):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time_zones: list = []
        for i in range(TimeZone.get_lowest_zone_value(), TimeZone.get_highest_zone_value() + 1):
            self.time_zones.append(TimeZone(i))
        self.twelve_hour_periods: tuple = ('a.m.', 'am', 'p.m.', 'pm')

    # TODO: documentation...
    @commands.command(description=HelpDescriptions.REMIND)
    async def remind(self, ctx: commands.Context, name, reminder_time: str, message: str = ""):
        reminder_response = "Your reminder has been successfully processed! " + \
                            "It will be sent at the specified time."
        current_guild = ctx.guild
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild.id)
        current_channel = self.bot.get_channel(reminder_channel_id)
        # TODO: I like this, but I wonder if I can further constrict the bounds to
        # only the roles available in Smorg's reminder channel.
        mentionables = [role.name for role in current_guild.roles if role.name == name] + \
                       [member.display_name for member in current_channel.members if member.display_name == name]
        if mentionables:
            selected_tag = self.select_tag(ctx, mentionables)
            if reminder_time:
                selected_time = self.select_time(ctx, reminder_time)
            else:
                reminder_response = "Error: that time is invalid. Please try again."
        else:
            reminder_response = "Error: that role is invalid. Please try again."
        await current_channel.send(reminder_response)

    async def select_tag(self, ctx: commands.Context, mentionables):
        chosen_mentionable: str = mentionables[0]
        chosen_mentionable_index: int = await Disambiguator.disambiguate(self.bot, ctx, mentionables)
        return chosen_mentionable[chosen_mentionable_index]

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
