import discord
from discord.ext import commands
from smorgasDB import Guild
from Cogs.Helpers.Enumerators.universalist import ColorConstants, HelpDescriptions


class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', description=HelpDescriptions.SUPPORT)
    async def support(self, ctx):
        """
        This method displays Smorg's help menu.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        support_embed = discord.Embed(
            title='Smorg Support',
            description='This bot supports the following commands:',
            color=ColorConstants.VIBRANT_PURPLE
        )
        sorted_commands = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        for command in sorted_commands:
            support_embed.add_field(
                name=f".{command.name}",
                value=command.description,
                inline=False
            )
        await ctx.send(embed=support_embed)

    @commands.command(description=HelpDescriptions.OBSERVE)
    async def observe(self, ctx, new_prefix):
        Guild.update_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"You've updated your Guild's prefix to '{new_prefix}'.")

    @observe.error
    async def observe_error(self, ctx, error):
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
