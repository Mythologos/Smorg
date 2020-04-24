# TODO: documentation

import datetime
from discord.ext import commands
from typing import Optional

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.embedder import Embedder
from Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from smorgasDB import Guild


class Helper(Chronologist, commands.Cog, Embedder):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command(name='help', description=HelpDescription.SUPPORT)
    async def support(self, ctx: commands.Context) -> None:
        """
        This method displays Smorg's help menu.
        :param ctx: The context from which the quotation came.
        :return: None
        """
        sorted_commands: list = sorted(self.bot.commands, key=lambda smorg_command: smorg_command.name)
        embed_items: dict = {"items": "commands", "color": ColorConstant.VIBRANT_PURPLE}
        field_items: dict = {"current_prefix": ctx.prefix}
        await self.embed(
            ctx.channel, sorted_commands, initialize_embed=self.initialize_itemized_embed,
            initialize_field=self.initialize_support_field, embed_items=embed_items, field_items=field_items
        )

    @staticmethod
    async def initialize_support_field(command: commands.Command, current_prefix: str):
        name: str = f"{current_prefix}{command.name}"
        description: str = f"{command.description}"
        inline: bool = False
        return name, description, inline

    @commands.command(description=HelpDescription.OBSERVE)
    async def observe(self, ctx: commands.Context, new_prefix: str) -> None:
        Guild.update_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"You've updated your Guild's prefix to '{new_prefix}'.")

    @commands.command(description=HelpDescription.PURGE)
    async def purge(self, ctx: commands.Context, message_count: Optional[int], from_time: Optional[str],
                    to_time: Optional[str]):
        additional_validators: tuple = (self.validate_past_datetime,)
        datetime_defaults: dict = {'default_minute': None, 'default_hour': None}
        start_time: datetime.datetime = await self.process_temporality(
            from_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators,
            default_generator=self.generate_dt_defaults_from_tz, manual_defaults=datetime_defaults
        ) if from_time else None

        end_time: datetime.datetime = await self.process_temporality(
            to_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators,
            default_generator=self.generate_dt_defaults_from_tz, manual_defaults=datetime_defaults
        ) if to_time else None

        history_args: dict = {}
        if start_time:
            start_time = await self.convert_to_naive_timezone(start_time)
            history_args["after"] = start_time
        if end_time:
            end_time = await self.convert_to_naive_timezone(end_time)
            history_args["before"] = end_time
        if message_count:
            history_args["limit"] = message_count
        elif not (start_time and end_time) and not message_count:
            message_count = 1
            history_args["limit"] = message_count

        delete_count: int = 0
        await ctx.message.delete()
        async for message in ctx.message.channel.history(**history_args):
            await message.delete()
            delete_count += 1
        else:
            await ctx.send(f"You've deleted up to {message_count or delete_count} messages just now.")
