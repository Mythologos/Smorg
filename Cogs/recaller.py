import discord
from discord.ext import commands
from smorgasDB import Guild


class Recaller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_zones: list = []
        self.twelve_hour_signifiers: list = []

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
            # if len(mentionables) > 1:
            #    mentionable_index = await select_from(ctx, mentionables)
            #    mentionables = [mentionables[mentionable_index]]
            # TODO: finish this with an interactive step to select in the case of ambiguity.
            tag = mentionables[0]
            # TODO: separate time handling into separate method(s)?
            reminder_time = reminder_time.split(',')
            if len(reminder_time) > 1:
                if len(reminder_time) > 2:
                    ...
                    # to military time & to a standardized time zone
                elif reminder_time[1] in self.twelve_hour_signifiers:
                    ...
                    # to military time
                elif reminder_time[1] in self.time_zones:
                    ...
                    # to a standardized time zone
            else:
                ...
                # TODO: handle time formatting.
                # "12:00 [P.M.] [EST], 01/04/2019"
        else:
            reminder_response = "Error: that role is invalid. Please try again."
        await current_channel.send(reminder_response)

    # TODO: issue --> fix time from decimal to hourly (e.g. /60).
    async def to_military_time(self, full_time):
        # type: (str) -> int
        time_offset: int = 1200
        time_components: list = full_time.split()
        try:
            time_components[0] = int(time_components[0].replace(':', ''))
        except ValueError:
            ...
            # call error instead of finishing
        else:
            if time_components[1] in ['pm', 'PM', 'p.m.', 'P.M.']:
                if time_components[0] >= 1300:
                    ...
                    # raise error.
                else:
                    time_components[0] += (time_components[0] - time_offset)
            elif time_components[1] in ['am', 'AM', 'a.m.', 'A.M.']:
                if time_components[0] >= 1300:
                    ...
                    # raise error
                elif time_components[0] >= 1200:
                    time_components[0] -= time_offset
        return time_components[0]

    # I like this, but I'm not sure how to proceed. I'll come back to it.
    # async def select_from(ctx, items):
        # selection_message = "Please select an item from the following options via its number: /n"
        # for index, item in enumerate(items):
        #     selection_message = selection_message + index + ": " + item + "/n"
        # await ctx.send(selection_message)
        # selected_index = ???
        # return selected_index
