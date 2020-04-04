# TODO: method to display server's quotes (and by author name)
# TODO: method to display server's reminders (a general timetable)
# TODO: method to display accepted roll syntax mechanics

import discord
from discord.ext import commands

from Cogs.Helpers.Enumerators.universalist import ColorConstants, HelpDescriptions


class Cataloguer:
    @commands.group(description=HelpDescriptions.DISPLAY)
    async def display(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument

    @display.error
    async def display_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        if isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Display): Missing Required Argument',
                    description=f'The given time zone is invalid.',
                    color=ColorConstants.ERROR_RED
                )
            else:
                error_embed = discord.Embed(
                    title='Error (Display): User Input Error',
                    description=f'The error type is: {error}. A better error message will be supplied soon.',
                    color=ColorConstants.ERROR_RED
                )
        else:
            error_embed = discord.Embed(
                title='Error (Display): Miscellaneous Error',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)
