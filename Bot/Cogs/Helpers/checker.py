"""
This module contains the checker Cog. It is a mix-in Cog that consists of checks as per discord.py's specifications.
"""

from discord.ext.commands import Context

from ...smorgasDB import Quote


class Checker:
    """
    This class consists of various checks that are performed by Smorg to assure the validity of its commands
    and their inputs.
    """
    @staticmethod
    async def is_yoinkable(ctx: Context) -> bool:
        """
        This method determines whether or not the yoink Command can work for a Guild.

        :param Context ctx: the context from which the command was made.
        :return bool: True if Smorg has quotes; False if not.
        """
        return Quote.count_quotes(ctx.guild.id) > 0
