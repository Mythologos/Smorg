"""
This module contains the Arranger Cog. This Cog contains the govern Command, which has the subcommands of
quotation, reminder, and gamble. Each of these subcommands set the channel in which relevant quotes,
reminders, and gambles (e.g. rolls) will be reported.
"""

import discord
from discord.ext import commands
from typing import Callable

from smorgasDB import Guild
from Cogs.Helpers.exceptioner import MissingSubcommand
from Cogs.Helpers.Enumerators.universalist import HelpDescription, StaticText


class Arranger(commands.Cog):
    """
    This Cog centers around the govern Command. This command manages the channels for which Smorg will output
    certain content. All subcommands of the govern Command use handle_domain to perform their necessary duties.
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.group(description=HelpDescription.GOVERN)
    async def govern(self, ctx: commands.Context) -> None:
        """
        This Command allows a user to alter the channel in which Smorg replies to various commands.
        Its subcommands include quotation, reminder, and gamble.

        :param commands.Context ctx: the context from which the command was made.
        """
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand

    @govern.command()
    async def quotation(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        This method allows users to alter the chat in which Smorg embeds its quotes.
        See the handle_domain function for further details.

        :param commands.Context ctx: the context from which the command was made.
        :param discord.TextChannel channel: the channel in which quotes will now be displayed.
        """
        await self.handle_domain(ctx, Guild.update_quotation_channel, channel.id, StaticText.GOVERN_QUOTATION_TEXT)

    @govern.command()
    async def reminder(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        This method allows users to alter the chat in which Smorg posts its reminders.
        See the handle_domain function for further details.

        :param commands.Context ctx: the context from which the command was made.
        :param discord.TextChannel channel: the channel in which reminders will now be displayed.
        """
        await self.handle_domain(ctx, Guild.update_reminder_channel, channel.id, StaticText.GOVERN_REMINDER_TEXT)

    @govern.command()
    async def gamble(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        This method allows users to alter the chat in which Smorg posts its public gambles.
        See the handle_domain function for further details.

        :param commands.Context ctx: the context from which the command was made.
        :param discord.TextChannel channel: the channel in which quotes will now be displayed.
        """
        await self.handle_domain(ctx, Guild.update_gamble_channel, channel.id, StaticText.GOVERN_GAMBLE_TEXT)

    async def handle_domain(self, ctx: commands.Context, table_update_method: Callable, channel_id: int,
                            govern_message: str) -> None:
        """
        This method allows users to alter the chats in which Smorg posts information.

        :param ctx: The context from which the command was made.
        :param table_update_method: The SmorgDB method which will update the relevant domain channel for Smorg.
        :param str govern_message: The message which Smorg reports back after updating the relevant domain channel.
        :param int channel_id: The ID of the channel which the user wants to designate as a domain for Smorg's messages.
        """
        current_guild: discord.Guild = ctx.guild
        table_update_method(current_guild.id, channel_id)
        await self.bot.get_channel(channel_id).send(govern_message)
