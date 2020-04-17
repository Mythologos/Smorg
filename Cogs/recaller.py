# TODO: documentation...
# TODO: I think PostgreSQL is doing something with the datetimes. They get to the database intact,
# but the database may handle them erroneously. This must be investigated.


import discord
import datetime

from discord.ext import commands
from typing import Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.exceptioner import MissingReminder
from Cogs.Helpers.Enumerators.universalist import ColorConstant, HelpDescription
from smorgasDB import Guild, Reminder


class Recaller(commands.Cog, Chronologist):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()

    @commands.command(description=HelpDescription.REMIND)
    async def remind(self, ctx: commands.Context, mentionable: Union[discord.Member, discord.Role],
                     reminder_time: str, message: str = "") -> None:
        current_guild_id = ctx.guild.id
        validated_datetime: datetime.datetime = await self.handle_time(reminder_time)
        Reminder.create_reminder_with(current_guild_id, mentionable.mention, message, validated_datetime)
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild_id)
        current_channel = self.bot.get_channel(reminder_channel_id) or ctx.message.channel
        await current_channel.send(
            "Your reminder has been successfully processed! It'll be sent at the specified time."
        )

    @commands.command(description=HelpDescription.REVISE)
    async def revise(self, ctx: commands.Context, mentionable: Union[discord.Member, discord.Role],
                     old_reminder_time: str, new_reminder_time: Optional[str] = None,
                     new_message: Optional[str] = None) -> None:
        current_guild_id = ctx.guild.id
        old_datetime: datetime.datetime = await self.handle_time(old_reminder_time)
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild_id)
        current_channel = self.bot.get_channel(reminder_channel_id) or ctx.message.channel
        if Reminder.has_reminder_at(current_guild_id, mentionable.mention, old_datetime):
            new_datetime: datetime.datetime = await self.handle_time(new_reminder_time)
            Reminder.update_reminder_with(current_guild_id, mentionable.mention, old_datetime, new_datetime, new_message)
            await current_channel.send(
                "Your revision has been successfully processed!"
            )
        else:
            raise MissingReminder

    @commands.command(description=HelpDescription.FORGET)
    async def forget(self, ctx: commands.Context, mentionable: Union[discord.Member, discord.Role],
                     reminder_time: str) -> None:
        mention: str = mentionable.mention
        current_guild_id = ctx.guild.id
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild_id)
        current_channel = self.bot.get_channel(reminder_channel_id) or ctx.message.channel
        validated_datetime: datetime.datetime = await self.handle_time(reminder_time)
        if Reminder.has_reminder_at(current_guild_id, mention, validated_datetime):
            Reminder.delete_reminder_with(current_guild_id, mention, validated_datetime)
            await current_channel.send(
                "Your deletion has been successfully processed!"
            )
        else:
            raise MissingReminder

    async def handle_time(self, reminder_time: str) -> datetime.datetime:
        default_tz: datetime.timezone = datetime.timezone.utc
        today: datetime.datetime = datetime.datetime.now(default_tz)
        additional_validators: tuple = (self.validate_future_datetime,)
        temporal_defaults: dict = {
            "default_hour": None, "default_minute": 0, "default_tz": default_tz, "default_day": today.day,
            "default_month": today.month, "default_year": today.year
        }
        validated_datetime: datetime.datetime = await self.process_temporality(
            reminder_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators, temporal_defaults=temporal_defaults
        )
        return validated_datetime

    @revise.error
    @forget.error
    async def reminder_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        command_name: str = ctx.command.name.title()
        error_embed: Union[discord.Embed, None] = None
        if isinstance(error, MissingReminder):
            error_embed = discord.Embed(
                title=f'Error ({command_name}): Missing Reminder',
                description='Your server does not have a reminder scheduled for that time and mention.',
                color=ColorConstant.ERROR_RED
            )
        if error_embed:
            await ctx.send(embed=error_embed)
