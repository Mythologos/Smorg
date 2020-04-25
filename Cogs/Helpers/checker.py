"""
...
"""
# describe as Cog mixin

from discord.ext.commands import Context

from smorgasDB import Quote


class Checker:
    @staticmethod
    async def is_yoinkable(ctx: Context) -> bool:
        """
        ...
        :param ctx:
        :return bool: ...
        """
        return (Quote.count_quotes(ctx.guild.id) - 1) >= 0
