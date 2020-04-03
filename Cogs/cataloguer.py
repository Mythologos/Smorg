# TODO: method to display server's quotes (and by author name)
# TODO: method to display server's reminders (a general timetable and by role)
# TODO: method to display accepted time zone list
# Maybe somehow incorporate this in other Cogs, making this like Disambiguator?
# That way, I could subclass display to many Cogs without making the functions related to said Cogs
# separate from their respective modules.

from discord.ext import commands

from Cogs.Helpers.Enumerators.universalist import HelpDescriptions


class Cataloguer:
    @staticmethod
    @commands.command(description=HelpDescriptions.DISPLAY)
    async def display(ctx: commands.Context):
        ...
