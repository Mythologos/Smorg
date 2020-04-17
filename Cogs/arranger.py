# TODO: documentation

import discord
from discord.ext import commands
from typing import Callable

from smorgasDB import Guild
from Cogs.Helpers.exceptioner import MissingSubcommand
from Cogs.Helpers.Enumerators.universalist import HelpDescription


class Arranger(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.group(description=HelpDescription.GOVERN)
    async def govern(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand

    @govern.command()
    async def quotation(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        This method allows users to alter the chat in which Smorg embeds its quotes.
        See the handle_domain function for further details.
        """
        govern_message = 'Congrats! You have successfully changed where I engrave your greatest sayings.'
        await self.handle_domain(ctx, Guild.update_quotation_channel, channel.id, govern_message)

    @govern.command()
    async def reminder(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        This method allows users to alter the chat in which Smorg posts its reminders.
        See the handle_domain function for further details.
        """
        govern_message = 'Congrats! You have successfully changed where I blare your noisiest pings.'
        await self.handle_domain(ctx, Guild.update_reminder_channel, channel.id, govern_message)

    @govern.command()
    async def gamble(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        This method allows users to alter the chat in which Smorg posts its public gambles.
        See the handle_domain function for further details.
        """
        govern_message = 'Congrats! You have successfully changed where you let the cards and dice fly.'
        await self.handle_domain(ctx, Guild.update_gamble_channel, channel.id, govern_message)

    async def handle_domain(self, ctx: commands.Context, table_update_method: Callable, channel_id: int,
                            govern_message: str):
        """
        This method allows users to alter the chats in which Smorg posts information.
        :param ctx: The context from which the request came.
        :param table_update_method: The SmorgDB method which will update the relevant domain channel for Smorg.
        :param govern_message: The message which Smorg reports back after updating the relevant domain channel.
        :param channel_id: The ID of the channel which the user wants to designate as a domain for Smorg's messages.
        :return: None.
        """
        current_guild = ctx.guild
        table_update_method(current_guild.id, channel_id)
        await self.bot.get_channel(channel_id).send(govern_message)
