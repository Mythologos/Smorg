# TODO: documentation...
# describe as Cog mixin

import discord

from smorgasDB import Quote


class Checker:
    @staticmethod
    async def is_yoinkable(ctx):
        return (Quote.count_quotes(ctx.guild.id) - 1) >= 0
