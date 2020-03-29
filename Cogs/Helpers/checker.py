# TODO: documentation...
# describe as Cog mixin

import discord
from discord.ext import commands

from smorgasDB import Quote


class Checker:
    @staticmethod
    async def is_yoinkable(ctx: commands.Context) -> bool:
        return (Quote.count_quotes(ctx.guild.id) - 1) >= 0
