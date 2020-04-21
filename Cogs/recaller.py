# TODO: documentation...
# TODO: I think PostgreSQL is doing something with the datetimes. They get to the database intact,
# but the database may handle them erroneously. This must be investigated.


import discord
import datetime

from discord.ext import commands
from sqlalchemy.exc import DataError
from typing import Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.exceptioner import Exceptioner, MissingReminder
from Cogs.Helpers.Enumerators.universalist import DiscordConstant, HelpDescription
from smorgasDB import Guild, Reminder


class Recaller(commands.Cog, Chronologist, Exceptioner):
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
            Reminder.update_reminder_with(
                current_guild_id, mentionable.mention, old_datetime, new_datetime, new_message
            )
            await current_channel.send("Your revision has been successfully processed!")
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
            await current_channel.send("Your deletion has been successfully processed!")
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

    @remind.error
    @revise.error
    @forget.error
    async def reminder_error(self, ctx: commands.Context, error: Exception) -> None:
        command_name: str = getattr(ctx.command.root_parent, "name", ctx.command.name).title()
        error = getattr(error, "original", error)
        error_name: str = await self.compose_error_name(error.__class__.__name__)
        error_description: Union[str, None] = None
        if isinstance(error, DataError):
            error_description = f'The provided reminder is too long. Please limit your reminder to ' \
                                f'{DiscordConstant.MAX_EMBED_FIELD_VALUE} characters.'
        elif isinstance(error, MissingReminder):
            error_description = 'Your server does not have a reminder scheduled for that time and mention.'
        elif not isinstance(error, discord.DiscordException):
            error_description = f'The error is a non-Discord error. It has the following message: {error}. ' \
                                f'It should be added and handled properly as soon as possible.'
        if error_description:
            error_embed: discord.Embed = await self.initialize_error_embed(command_name, error_name, error_description)
            await ctx.send(embed=error_embed)
