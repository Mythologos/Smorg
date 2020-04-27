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

        :param Context ctx: the context from which the command was made.
        :return bool: ...
        """
        return (Quote.count_quotes(ctx.guild.id) - 1) >= 0
