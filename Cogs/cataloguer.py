# TODO: method to display accepted roll syntax mechanics

import datetime
import discord
from discord.ext import commands
from typing import Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.embedder import Embedder
from Cogs.Helpers.exceptioner import EmptyEmbed
from Cogs.Helpers.Enumerators.timekeeper import TimeZone
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions
from Cogs.Helpers.Enumerators.tabulator import MathematicalOperator, MathematicalFunction
from smorgasDB import Quote, Reminder


class Cataloguer(commands.Cog, Chronologist, Embedder):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()

    @commands.group(description=HelpDescriptions.DISPLAY)
    async def display(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument

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
        embed_items: dict = {
            "item_author": reminder_name,
            "items": "reminders",
            "color": ColorConstants.CALM_GREEN
        }
        await self.embed(ctx, reminder_list, initialize_embed=self.initialize_authored_embed,
                         initialize_field=self.initialize_reminder_field, embed_items=embed_items)

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
        embed_items: dict = {
            "item_author": overall_name or ctx.guild.name,
            "items": "quotes",
            "color": ColorConstants.HEAVENLY_YELLOW
        }
        field_items: dict = {"overall_author": overall_name}
        await self.embed(
            ctx, quote_list, initialize_embed=self.initialize_authored_embed,
            initialize_field=self.initialize_quote_field,
            embed_items=embed_items, field_items=field_items
        )

    @staticmethod
    async def initialize_authored_embed(item_author: str, items: str, color: ColorConstants, page_number: int = 0):
        if not page_number:
            desc: str = f'{items.title()} by {item_author} include:'
        else:
            desc = f'Further {items} by {item_author} consist of:'
        page_number: int = (page_number // DiscordConstants.MAX_EMBED_FIELDS) + 1
        quote_embed: discord.Embed = discord.Embed(
            title=f"The {items.title()} of {item_author}, Page {page_number}",
            description=desc,
            color=color
        )
        return quote_embed

    # TODO: maybe combine with the zones embed-creator
    @staticmethod
    async def initialize_arithmetic_embed(items: str, page_number: int = 0):
        if not page_number:
            desc: str = f'The {items} supported by Smorg include:'
        else:
            desc = f'Further {items} that Smorg supports consist of:'
        page_number: int = (page_number // DiscordConstants.MAX_EMBED_FIELDS) + 1
        operator_embed: discord.Embed = discord.Embed(
            title=f"Smorg's {items.title()}, Page {page_number}",
            description=desc,
            color=ColorConstants.NEUTRAL_ORANGE
        )
        return operator_embed

    @staticmethod
    async def initialize_arithmetic_field(name: str, representation: str) -> tuple:
        name = f"{name.title().replace('_', ' ')}"
        value = f"Representation: {representation}"
        if representation.isalpha():
            value += '()'
        inline: bool = False
        return name, value, inline

    @display.command()
    async def operators(self, ctx: commands.Context) -> None:
        operator_list: list = [(item.name, item.symbol) for item in MathematicalOperator.__members__.values()]
        embed_items: dict = {
            "items": "operators"
        }
        await self.embed(
            ctx, operator_list, initialize_embed=self.initialize_arithmetic_embed,
            initialize_field=self.initialize_arithmetic_field, embed_items=embed_items
        )

    @display.command()
    async def functions(self, ctx: commands.Context) -> None:
        function_list: list = [(item.name, item.representation) for item in MathematicalFunction.__members__.values()]
        embed_items: dict = {
            "items": "functions"
        }
        await self.embed(
            ctx, function_list, initialize_embed=self.initialize_arithmetic_embed,
            initialize_field=self.initialize_arithmetic_field, embed_items=embed_items
        )

    # TODO: handle error where invalid subcommand argument is given (TypeError?)
    @display.error
    @operators.error
    @reminders.error
    @quotes.error
    @zones.error
    async def display_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        if isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Display): Missing Required Argument',
                    description=f'A required argument is missing from your command.',  # TODO: improve message
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
