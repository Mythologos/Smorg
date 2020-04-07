# TODO: method to display server's reminders (a general timetable)
# TODO: method to display accepted roll syntax mechanics

import datetime
import discord
from discord.ext import commands
from typing import Any, Callable, Iterable, List, Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.exceptioner import EmptyEmbed
from Cogs.Helpers.Enumerators.timekeeper import TimeZone
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

    # Embed Pseudocode:
    # general method setup:
    # retrieve input from source
    # sort data by some criterion
    # enumerate data
    # for loop
    #   if 26th field:
    #       send embed 1
    #       create new embed
    #   add embed field
    # else
    #   if embed empty
    #       send default embed and/or error (undecided)
    # send final embed

    # TODO: likely move this out of this class, as embedding could be used by things like gambler
    # for non-display commands.
    @staticmethod
    async def embed(ctx: commands.Context, sorted_data: List[Any], initialize_embed: Callable,
                    initialize_field: Callable, embed_items: Union[dict, None] = None,
                    field_items: Union[dict, None] = None) -> None:
        enumerated_data: enumerate = enumerate(sorted_data)
        data_embed: discord.Embed = await initialize_embed(**embed_items) if embed_items else await initialize_embed()
        for counter, contents in enumerated_data:
            if counter and (counter % DiscordConstants.MAX_EMBED_FIELDS) == 0:
                await ctx.send(embed=data_embed)
                data_embed = await initialize_embed(**embed_items, page_number=counter) if embed_items \
                    else await initialize_embed(counter)
            if isinstance(contents, Iterable):
                name, value, inline = await initialize_field(*contents, **field_items) if field_items \
                    else await initialize_field(*contents)
            else:
                name, value, inline = await initialize_field(contents, **field_items) \
                    if isinstance(contents, Iterable) else await initialize_field(contents)
            data_embed.add_field(name=name, value=value, inline=False)
        else:
            if len(data_embed.fields) == 0:
                raise EmptyEmbed
        await ctx.send(embed=data_embed)

    @staticmethod
    async def initialize_zone_embed(page_number: int = 0) -> discord.Embed:
        if not page_number:
            desc: str = 'Smorg supports the following time zones:'
        else:
            desc = 'Smorg also supports the following time zones:'
        page_number: int = (page_number // DiscordConstants.MAX_EMBED_FIELDS) + 1
        time_zone_embed = discord.Embed(
            title=f'Time Zone Aliases by GMT Offset, Page {page_number}',
            description=desc,
            color=ColorConstants.NEUTRAL_ORANGE
        )
        return time_zone_embed

    @staticmethod
    async def initialize_zone_field(time_zone: TimeZone) -> tuple:
        name = f"Zone {time_zone.value}"
        value = ", ".join(time_zone.aliases) if time_zone.aliases else "None"
        inline: bool = False
        return name, value, inline

    @display.command()
    async def zones(self, ctx: commands.Context) -> None:
        sorted_time_zones = sorted(self.time_zones, key=lambda tz: tz.value)
        await self.embed(ctx, sorted_time_zones, initialize_embed=self.initialize_zone_embed,
                         initialize_field=self.initialize_zone_field)

    # TODO: see if reminder and quote embeds can be merged, as their code is pretty similar.
    @staticmethod
    async def initialize_reminder_embed(reminder_name: str, page_number: int = 0) -> discord.Embed:
        if not page_number:
            desc: str = f'The upcoming reminders related to {reminder_name} are:'
        else:
            desc = f'Further upcoming reminders related to {reminder_name} are:'
        page_number: int = (page_number // DiscordConstants.MAX_EMBED_FIELDS) + 1
        reminder_embed: discord.Embed = discord.Embed(
            title=f"The Reminders of {reminder_name}, Page {page_number}",
            description=desc,
            color=ColorConstants.CALM_GREEN
        )
        return reminder_embed

    @staticmethod
    async def initialize_reminder_field(reminder_datetime: datetime.datetime, reminder_message: str) -> tuple:
        name = f"Reminder at {reminder_datetime.strftime(r'%H:%M UTC%Z on %d %b %Y')}"
        value = f"{reminder_message}"
        inline: bool = False
        return name, value, inline

    @display.command()
    async def reminders(self, ctx: commands.Context,
                        mentionable: Optional[Union[discord.Member, discord.Role]] = None) -> None:
        mention = mentionable.mention if mentionable else ctx.message.author.mention
        reminder_name: str = mentionable.name if mentionable else ctx.message.author.name
        reminder_list: list = Reminder.get_reminders_by(ctx.guild.id, mention)
        embed_items: dict = {"reminder_name": reminder_name}
        await self.embed(ctx, reminder_list, initialize_embed=self.initialize_reminder_embed,
                         initialize_field=self.initialize_reminder_field, embed_items=embed_items)

    # TODO: see if reminder and quote embeds can be merged, as their code is pretty similar.
    @staticmethod
    async def initialize_quote_embed(quote_author: str, page_number: int = 0) -> discord.Embed:
        if not page_number:
            desc: str = f'The quotes authored by {quote_author} are:'
        else:
            desc = f'Further quotes authored by {quote_author} are:'
        page_number: int = (page_number // DiscordConstants.MAX_EMBED_FIELDS) + 1
        quote_embed: discord.Embed = discord.Embed(
            title=f"The Quotes of {quote_author}, Page {page_number}",
            description=desc,
            color=ColorConstants.HEAVENLY_YELLOW
        )
        return quote_embed

    @staticmethod
    async def initialize_quote_field(quote_author: str, quote: str, overall_author: str):
        name = None
        value = f"\"{quote}\" -- {quote_author if quote_author != overall_author else (overall_author or 'Anonymous')}"
        inline: bool = False
        return name, value, inline

    @display.command()
    async def quotes(self, ctx: commands.Context, author: Union[discord.Member, str, None]) -> None:
        overall_name = author.name if isinstance(author, discord.Member) else author
        quote_list: list = Quote.get_quotes_by(g_id=ctx.guild.id, auth=overall_name)
        embed_items = {"quote_author": overall_name or ctx.guild.name}
        field_items = {"overall_author": overall_name}
        await self.embed(ctx, quote_list, initialize_embed=self.initialize_quote_embed,
                         initialize_field=self.initialize_quote_field, embed_items=embed_items,
                         field_items=field_items)

    # TODO: handle error where invalid subcommand argument is given (TypeError?)
    @display.error
    @reminders.error
    @quotes.error
    @zones.error
    async def display_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        if isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Display): Missing Required Argument',
                    description=f'A required argument is missing from your command.',  # TODO: improve message?
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, EmptyEmbed):  # TODO: maybe change error type, not sure if it fits here
                error_embed = discord.Embed(
                    title='Error (Display): Empty Embed',
                    description=f'The display that you requested has no data to fill it.',
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
