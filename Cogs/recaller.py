import discord
from discord.ext import commands
from smorgasDB import Guild
from .Helpers.time_zone import TimeZone


class Recaller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_zones: list = []
        for i in range(-12, 14):
            self.time_zones.append(TimeZone(i))
        self.twelve_hour_signifiers: tuple = ('a.m.', 'am', 'p.m.', 'pm')

    # TODO: documentation...
    @commands.command(description="This command signals a role at a certain time with a certain message. " +
                                  "It takes arguments in the order of role, time, and an optional message. " +
                                  "Time can be in terms of a twelve-hour or twenty-four-hour clock; " +
                                  "however, if it is the former, it must be in quotes with an A.M. or P.M. " +
                                  "accompanying it. Roles and messages consisting of multiple words should also be in quotes.")
    async def remind(self, ctx, name, reminder_time, message=''):
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

    async def select_tag(self, ctx, mentionables):
        chosen_mentionable: str = mentionables[0]
        if len(mentionables) > 1:
            selection_message: str = "Please select an item from the following options via its number: /n"
            for index, mentionable in enumerate(mentionables):
                selection_message = selection_message + str(index) + ": " + mentionable + "/n"
            await ctx.send(selection_message)
            try:
                mentionable_index = await self.bot.wait_for('message', timeout=120.0,
                                                            check=lambda msg:
                                                            (msg.author == ctx.author) and
                                                            (0 <= int(msg) < len(mentionables)))
                chosen_mentionable = mentionables[mentionable_index]
            except TimeoutError:
                disambiguation_timeout_embed = discord.Embed(title='Error (Remind): Disambiguation Timeout',
                                                             description='You didn\'t supply a valid index quickly enough.',
                                                             color=0xB80000)
                await ctx.send(embed=disambiguation_timeout_embed)
        return chosen_mentionable

    async def select_time(self, ctx, reminder_time):
        datetime_components = reminder_time.split(',')
        try:
            full_time: list = datetime_components[0].split(':')
            hours: int = int(full_time[0])
            minutes: int = int(full_time[1])
        except ValueError:
            invalid_time_embed = discord.Embed(title='Error (Remind): Invalid Time Formatting',
                                               description='You didn\'t give a correctly-formatted time.',
                                               color=0xB80000)
            await ctx.send(embed=invalid_time_embed)
        else:
            if len(datetime_components) > 1:
                if len(datetime_components) > 2:
                    period: str = datetime_components[1]
                    time_zone: str = datetime_components[2]
                    hours, minutes = self.convert_to_military_time(hours, minutes, period)
                    hours, minutes = self.convert_to_absolute_time(hours, minutes, time_zone)
                    # to military time & to a standardized time zone
                elif reminder_time[1] in self.twelve_hour_signifiers:
                    period: str = datetime_components[1]
                    hours, minutes = self.convert_to_military_time(hours, minutes, period)
                    # to military time
                elif reminder_time[1] in self.time_zones:
                    time_zone: str = datetime_components[1]
                    hours, minutes = self.convert_to_absolute_time(hours, minutes, time_zone)
                    # to a standardized time zone
                else:
                    ...
                    # TODO: handle time formatting.
                    # TIME: "12:00 [P.M.] [EST]"
                    # DATE: "4 January 2019"
            return hours, minutes

    @staticmethod
    async def convert_to_military_time(hours, minutes, period):
        # type: (int, int, str) -> tuple
        if period in ['pm', 'p.m.']:
            if ...:     # time is impossible
                ...
                # raise error.
            else:
                ...
                # increment time
        elif period in ['am', 'a.m.']:
            if ...:     # time is impossible
                ...
                # raise error
            elif ...:   # time is possible, special case
                ...     # decrement time
        return hours, minutes

    # TODO: change method name?
    @staticmethod
    async def convert_to_absolute_time(hours, minutes, time_zone):
        ...
