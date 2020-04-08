# TODO: documentation

import datetime
import discord
from discord.ext import commands
from typing import Optional

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions
from smorgasDB import Guild


class Helper(Chronologist, commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command(name='help', description=HelpDescriptions.SUPPORT)
    async def support(self, ctx: commands.Context):
        """
        This method displays Smorg's help menu.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        support_embed = discord.Embed(
            title='Smorg Support, Page 1',
            description='This bot supports the following commands:',
            color=ColorConstants.VIBRANT_PURPLE
        )
        sorted_commands = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        for counter, command in enumerate(sorted_commands):
            if counter and (counter % DiscordConstants.MAX_EMBED_FIELDS) == 0:
                await ctx.send(embed=support_embed)
                support_embed = discord.Embed(
                    title=f'Smorg Support, Page {(counter // DiscordConstants.MAX_EMBED_FIELDS) + 1}',
                    description='This bot also supports these commands:',
                    color=ColorConstants.VIBRANT_PURPLE
                )
            support_embed.add_field(
                name=f".{command.name}",
                value=command.description,
                inline=False
            )
        await ctx.send(embed=support_embed)

    @commands.command(description=HelpDescriptions.OBSERVE)
    async def observe(self, ctx: commands.Context, new_prefix: str) -> None:
        Guild.update_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"You've updated your Guild's prefix to '{new_prefix}'.")

    @observe.error
    async def observe_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(
                title='Error (Observe): Missing Prefix',
                description='You didn\'t supply a prefix.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Observe): Unfinished Quotation',
                description='You forgot a closing quotation mark on your prefix.',
                color=ColorConstants.ERROR_RED
            )
        else:
            error_embed = discord.Embed(
                title='Error (Observe)',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)

    # TODO: the remaining issue here is that from_time and to_time can be aware, which doesn't work with history.
    # This needs to be fixed. This may require a different approach than process_datetime.
    # It may be possible to make process_datetime more flexible by accepting functional arguments.
    # For example, it could accept: a parser, a main validator, and a list of other validating functions.
    # This is alongside one or multiple dicts of optional values.
    @commands.command(description=HelpDescriptions.PURGE)
    async def purge(self, ctx: commands.Context, message_count: Optional[int],
                    from_time: Optional[str], to_time: Optional[str]):
        today: datetime.datetime = datetime.datetime.today()
        datetime_defaults: dict = {'default_minute': None, 'default_hour': None, 'default_day': today.day,
                                   'default_month': today.month, 'default_year': today.year, 'default_tz': None}
        await ctx.message.delete()
        if from_time and to_time:
            start_time: datetime.datetime = await self.process_datetime(from_time, **datetime_defaults)
            end_time: datetime.datetime = await self.process_datetime(to_time, **datetime_defaults)
            async for message in ctx.message.channel.history(before=start_time, after=end_time, limit=message_count):
                await message.delete()
            await ctx.send(f"You've deleted up to {message_count} messages just now.")
        elif from_time:
            start_time: datetime.datetime = await self.process_datetime(from_time, **datetime_defaults)
            if not message_count:
                message_count: int = 1
            async for message in ctx.message.channel.history(after=start_time, limit=message_count):
                await message.delete()
            await ctx.send(f"You've deleted up to {message_count} messages just now.")
        elif message_count:
            async for message in ctx.message.channel.history(limit=message_count):
                await message.delete()
            await ctx.send(f"You've deleted up to {message_count} messages just now.")
        else:
            message_count = 1
            async for message in ctx.message.channel.history(limit=message_count):
                await message.delete()
            await ctx.send(f"You've deleted up to {message_count} messages just now.")
