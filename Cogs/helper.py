import discord
from discord.ext import commands


class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='This command retrieves the menu below shown here.')
    async def support(self, ctx):
        """
        This method displays Smorg's help menu.
        :param ctx: The context from which the quotation came.
        :return: None.
        """
        support_embed = discord.Embed(title='Smorg Support',
                                      description='This bot supports the following commands:',
                                      color=0x20409A)
        sorted_commands = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        for command in sorted_commands:
            support_embed.add_field(name='.' + command.name, value=command.description, inline=False)
        await ctx.send(embed=support_embed)
