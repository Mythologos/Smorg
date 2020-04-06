# TODO: method to display server's reminders (a general timetable)
# TODO: method to display accepted roll syntax mechanics

import datetime
import discord
from discord.ext import commands
from typing import Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions
from smorgasDB import Quote, Reminder


class Cataloguer(commands.Cog, Chronologist):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()

    @commands.group(description=HelpDescriptions.DISPLAY)
    async def display(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument

    # TODO: handle error where invalid subcommand argument is given (TypeError?)
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

    @display.command()
    async def quotes(self, ctx: commands.Context, author: Union[discord.Member, str, None]) -> None:
        author = author.name if isinstance(author, discord.Member) else author
        quote_list: list = Quote.get_quotes_by(g_id=ctx.guild.id, auth=author)
        quote_embed: discord.Embed = discord.Embed(
            title=f"The Quotes of {author or ctx.guild.name}, Page 1",
            description=f"The quotes related to this {'author' if author else 'guild'} are:",
            color=ColorConstants.HEAVENLY_YELLOW
        )
        for counter, (quote_author, quote) in enumerate(quote_list):
            if counter and counter % DiscordConstants.MAX_EMBED_FIELDS == 0:
                await ctx.send(embed=quote_embed)
                quote_embed: discord.Embed = discord.Embed(
                    title=f"The Quotes of {author or ctx.guild.name}, "
                          f"Page {(counter // DiscordConstants.MAX_EMBED_FIELDS) + 1}",
                    description=f"Further quotes related to {author or ctx.guild.name} are:",
                    color=ColorConstants.HEAVENLY_YELLOW
                )
            quote_embed.add_field(
                name=f"Quote {counter + 1}",
                value=f"\"{quote}\" -- {quote_author if quote_author != author else (author or 'Anonymous')}",
                inline=False
            )
        else:
            # TODO: raise error instead?
            if len(quote_embed.fields) == 0:
                quote_embed.add_field(
                    name="Result",
                    value=f"No quotes are available for {author or ctx.guild.name}.",
                    inline=False
                )
        await ctx.send(embed=quote_embed)

    @display.command()
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

    @display.command()
    async def reminders(self, ctx: commands.Context,
                        mentionable: Optional[Union[discord.Member, discord.Role]] = None) -> None:
        mention = mentionable.mention if mentionable else ctx.message.author.mention
        reminder_list: list = Reminder.get_reminders_by(ctx.guild.id, mention)
        reminder_embed: discord.Embed = discord.Embed(
            name=f"The Reminders of {mentionable.name}, Page 1",
            description="The upcoming reminders related to this mentionable are:",
            color=ColorConstants.CALM_GREEN
        )
        for counter, (reminder_datetime, reminder_message) in enumerate(reminder_list):
            if counter and counter % DiscordConstants.MAX_EMBED_FIELDS == 0:
                await ctx.send(embed=reminder_embed)
                reminder_embed: discord.Embed = discord.Embed(
                    name=f"The Reminders of {mentionable.name}, "
                         f"Page {(counter // DiscordConstants.MAX_EMBED_FIELDS) + 1}",
                    description="Further upcoming reminders related to this member or role are:",
                    color=ColorConstants.CALM_GREEN
                )
            reminder_embed.add_field(
                name=f"Reminder at {reminder_datetime.strftime(r'%H:%M UTC%Z on %d %b %Y')}",
                value=f"{reminder_message}",
                inline=False
            )
        else:
            # TODO: raise error instead?
            if len(reminder_embed.fields) == 0:
                today = datetime.datetime.now(tz=datetime.timezone.utc)
                reminder_embed.add_field(
                    name=f"Result at {today.strftime(r'%H:%M %Z on %d %b %Y')}",
                    value="No reminders are available for this member or role.",
                    inline=False
                )
        await ctx.send(embed=reminder_embed)
