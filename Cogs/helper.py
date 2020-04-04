# TODO: documentation

import discord
from discord.ext import commands
from typing import Optional

from smorgasDB import Guild
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions


class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    # TODO: add ability to use time instead of a message count;
    # integrates well with history function's optional args
    # extract time validation from recaller, use as mix-in here.
    # use Optional from typing here
    # add: last_message_time: str = None, user: str = None
    @commands.command(description=HelpDescriptions.PURGE)
    async def purge(self, ctx: commands.Context, message_count: int = 1):
        async for message in ctx.message.channel.history(limit=message_count + 1):
            await message.delete()
        await ctx.send(f"You've deleted up to {message_count} messages just now.")

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
