"""
This module contains the helper Cog, which consists of various utility functions for Smorg's usage.
This includes the support function (aliased as "help"), the observe function, and the purge function.
"""

from datetime import datetime
from discord.ext import commands
from typing import Optional

from Bot.Cogs.Helpers.chronologist import Chronologist
from Bot.Cogs.Helpers.embedder import Embedder
from Bot.Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from Bot.smorgasDB import Guild


class Helper(Chronologist, commands.Cog, Embedder):
    """
    This class aids in providing users with basic bot utilities. It does so through three functions.
    The first is support, Smorg's help Command (accessed by the "help" keyword).
    The second is observe, which switches the prefix that a Guild's Commands must be preceded by.
    The third is purge, which deletes a certain number of previous messages and/or messages between designated times.
    """
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command(name='help', description=HelpDescription.SUPPORT)
    async def support(self, ctx: commands.Context) -> None:
        """
        This method uses the embed() function to display a list of Smorg's public commands.
        It is this bot's basic help display.

        :param commands.Context ctx: the context from which the command was made.
        """
        sorted_commands: list = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        embed_items: dict = {"items": "commands", "color": ColorConstant.VIBRANT_PURPLE}
        field_items: dict = {"current_prefix": ctx.prefix}
        await self.embed(
            ctx.channel, sorted_commands, initialize_embed=self.initialize_itemized_embed,
            initialize_field=self.initialize_support_field, embed_items=embed_items, field_items=field_items
        )

    @staticmethod
    async def initialize_support_field(command: commands.Command, current_prefix: str) -> tuple:
        """
        This method creates the main attributes of a field for an Embed object to display Command information.

        :param commands.Command command: a given Command belonging to Smorg.
        :param str current_prefix: the prefix that Smorg uses for the given Guild.
        :return tuple: two strings and a Boolean for the three keyword arguments of an Embed field.
        """
        name: str = f"{current_prefix}{command.name}"
        description: str = f"{command.description}"
        inline: bool = False
        return name, description, inline

    @commands.command(description=HelpDescription.OBSERVE)
    async def observe(self, ctx: commands.Context, new_prefix: str) -> None:
        """
        This method alters the prefix that Smorg uses for a given Guild.

        :param commands.Context ctx: the context from which the command was made.
        :param str new_prefix: the new prefix that Smorg will use to identify a certain Guild's Command calls.
        """
        Guild.update_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"You've updated your Guild's prefix to '{new_prefix}'.")

    @commands.command(description=HelpDescription.PURGE)
    async def purge(self, ctx: commands.Context, message_count: Optional[int], from_time: Optional[str],
                    to_time: Optional[str]) -> None:
        """
        This method deletes messages based on a given set of parameters.
        If nothing is given, the previous message is deleted.
        If a number is given, that number of previous messages are deleted.
        If a time or times are given, the messages deleted are based on those times;
        two times means that all times between such times will be deleted so long as
        a message count is not given.

        Times should be written as they are designated in the recaller.py module.

        :param commands.Context ctx: the context from which the command was made.
        :param Optional[int] message_count: a number of messages to be deleted (or an upper limit).
        :param Optional[str] from_time: the time after which messages should be deleted.
        :param Optional[str] to_time: the time before which messages should be deleted.
        """
        additional_validators: tuple = (self.validate_past_datetime,)
        datetime_defaults: dict = {'default_minute': None, 'default_hour': None}
        start_time: datetime = await self.process_temporality(
            from_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators,
            default_generator=self.generate_dt_defaults_from_tz, manual_defaults=datetime_defaults
        ) if from_time else None
        end_time: datetime = await self.process_temporality(
            to_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators,
            default_generator=self.generate_dt_defaults_from_tz, manual_defaults=datetime_defaults
        ) if to_time else None
        history_args: dict = {}
        if start_time:
            start_time = await self.convert_to_naive_timezone(start_time)
            history_args["after"] = start_time
        if end_time:
            end_time = await self.convert_to_naive_timezone(end_time)
            history_args["before"] = end_time
        if message_count:
            history_args["limit"] = message_count
        elif not (start_time and end_time) and not message_count:
            message_count = 1
            history_args["limit"] = message_count
        delete_count: int = 0
        await ctx.message.delete()
        async for message in ctx.channel.history(**history_args):
            await message.delete()
            delete_count += 1
        else:
            await ctx.send(f"You've deleted up to {message_count or delete_count} messages just now.")
