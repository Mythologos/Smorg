# TODO: documentation

import datetime
import discord
from discord.ext import commands
from typing import Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.embedder import Embedder
from Cogs.Helpers.exceptioner import EmptyEmbed, Exceptioner, MissingSubcommand
from Cogs.Helpers.Enumerators.croupier import RollMechanic
from Cogs.Helpers.Enumerators.tabulator import MathematicalOperator, MathematicalFunction
from Cogs.Helpers.Enumerators.timekeeper import TimeZone
from Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from smorgasDB import Quote, Reminder


class Cataloguer(commands.Cog, Chronologist, Embedder, Exceptioner):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()

    @commands.group(description=HelpDescription.DISPLAY)
    async def display(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand

    @staticmethod
    async def initialize_zone_field(time_zone: TimeZone) -> tuple:
        name = f"Zone {time_zone.value}"
        value = ", ".join(time_zone.aliases) if time_zone.aliases else "None"
        inline: bool = False
        return name, value, inline

    @display.command()
    async def zones(self, ctx: commands.Context) -> None:
        sorted_time_zones = sorted(self.time_zones, key=lambda tz: tz.value)
        embed_items: dict = {
            "items": "time zones",
            "color": ColorConstant.NEUTRAL_ORANGE
        }
        await self.embed(ctx.channel, sorted_time_zones, initialize_embed=self.initialize_itemized_embed,
                         initialize_field=self.initialize_zone_field, embed_items=embed_items)

    @staticmethod
    async def initialize_reminder_field(reminder_datetime: datetime.datetime, reminder_message: str, counter: int) -> \
            tuple:
        name = f"Reminder {counter + 1}, Scheduled at {reminder_datetime.strftime(r'%H:%M UTC%Z on %d %b %Y')}"
        value = f"{reminder_message or '[No Message Provided]'}"
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
            "color": ColorConstant.CALM_GREEN
        }
        field_items: dict = {"counter": None}
        await self.embed(ctx.channel, reminder_list, initialize_embed=self.initialize_authored_embed,
                         initialize_field=self.initialize_reminder_field, embed_items=embed_items,
                         field_items=field_items)

    @staticmethod
    async def initialize_quote_field(quote_author: str, quote: str, overall_author: str, counter: int) -> tuple:
        name = f"Quote {counter + 1}"
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
            "color": ColorConstant.HEAVENLY_YELLOW
        }
        field_items: dict = {"counter": None, "overall_author": overall_name}
        await self.embed(
            ctx.channel, quote_list, initialize_embed=self.initialize_authored_embed,
            initialize_field=self.initialize_quote_field,
            embed_items=embed_items, field_items=field_items
        )

    @staticmethod
    async def initialize_arithmetic_field(name: str, representation: str) -> tuple:
        name = f"{name.title().replace('_', ' ')}"
        value = f"Symbol: {representation}"
        if representation.isalpha():
            value += '()'
        inline: bool = False
        return name, value, inline

    @display.command()
    async def operators(self, ctx: commands.Context) -> None:
        operator_list: list = [(item.name, item.symbol) for item in MathematicalOperator.__members__.values()]
        embed_items: dict = {
            "items": "operators",
            "color": ColorConstant.NEUTRAL_ORANGE
        }
        await self.embed(
            ctx.channel, operator_list, initialize_embed=self.initialize_itemized_embed,
            initialize_field=self.initialize_arithmetic_field, embed_items=embed_items
        )

    @display.command()
    async def functions(self, ctx: commands.Context) -> None:
        function_list: list = [(item.name, item.representation) for item in MathematicalFunction.__members__.values()]
        embed_items: dict = {
            "items": "functions",
            "color": ColorConstant.NEUTRAL_ORANGE
        }
        await self.embed(
            ctx.channel, function_list, initialize_embed=self.initialize_itemized_embed,
            initialize_field=self.initialize_arithmetic_field, embed_items=embed_items
        )

    @display.command()
    async def dice(self, ctx: commands.Context):
        dice_mechanic_list: list = [(item.name, item.representation, item.value_range, item.description)
                                    for item in RollMechanic.__members__.values()]
        await self.embed(
            ctx.channel, dice_mechanic_list, initialize_embed=self.initialize_dice_embed,
            initialize_field=self.initialize_dice_field
        )

    @staticmethod
    async def initialize_dice_embed(page_number: int = 1) -> discord.Embed:
        if page_number == 1:
            desc: str = f'The form of the dice roll can be represented by \'x[dD]y[kKdD]z![<>]a\',' \
                        f'where the only required components are x, one of d or D, and y. The breakdown of each item ' \
                        f'in this roll is given below:'
        else:
            desc = f'More of Smorg\'s dice mechanics are as follows:'
        dice_mechanic_embed: discord.Embed = discord.Embed(
            title=f"Smorg's Dice Mechanics, Page {page_number}",
            description=desc,
            color=ColorConstant.NEUTRAL_ORANGE
        )
        return dice_mechanic_embed

    @staticmethod
    async def initialize_dice_field(name: str, representation: str, value_range: str, description: str) -> tuple:
        name: str = f"{name.title().replace('_', ' ')}, Representation: {representation}"
        value: str = f"{value_range} {description}"
        inline: bool = False
        return name, value, inline

    @dice.error
    @display.error
    @operators.error
    @reminders.error
    @quotes.error
    @zones.error
    async def display_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        command_name: str = ctx.command.name.title()
        error_name: str = await self.compose_error_name(error.__class__.__name__)
        error_description: Union[str, None] = None
        if isinstance(error, EmptyEmbed):
            error_description: str = 'The display that you requested has no data to fill it.'
        if error_description:
            error_embed: discord.Embed = await self.initialize_error_embed(command_name, error_name, error_description)
            await ctx.send(embed=error_embed)
