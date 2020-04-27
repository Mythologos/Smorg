"""
...
"""

from datetime import datetime
from discord import DiscordException, Embed, Member, Role, TextChannel
from discord.ext import commands, tasks
from sqlalchemy.exc import DataError
from typing import Optional, Union

from Cogs.Helpers.chronologist import Chronologist
from Cogs.Helpers.exceptioner import Exceptioner, MissingReminder
from Cogs.Helpers.Enumerators.universalist import DiscordConstant, HelpDescription, StaticText
from smorgasDB import Guild, Reminder


class Recaller(commands.Cog, Chronologist, Exceptioner):
    """
    ...
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()
        self.check_reminders.start()

    @commands.command(description=HelpDescription.REMIND)
    async def remind(self, ctx: commands.Context, mentionable: Union[Member, Role], reminder_time: str,
                     message: str = "") -> None:
        """
        ...

        :param commands.Context ctx: the context from which the command was made.
        :param Union[Member, Role] mentionable:
        :param str reminder_time:
        :param str message:
        """
        current_guild_id = ctx.guild.id
        validated_datetime: datetime = await self.handle_time(reminder_time)
        Reminder.create_reminder_with(current_guild_id, mentionable.mention, message, validated_datetime)
        reminder_channel_id: Union[int, None] = Guild.get_reminder_channel_by(current_guild_id)
        current_channel: TextChannel = self.bot.get_channel(reminder_channel_id) or ctx.message.channel
        await current_channel.send(StaticText.REMINDER_NOTIFICATION)

    @commands.command(description=HelpDescription.REVISE)
    async def revise(self, ctx: commands.Context, mentionable: Union[Member, Role], old_reminder_time: str,
                     new_reminder_time: Optional[str] = None, new_message: Optional[str] = None) -> None:
        """
        ...

        :param commands.Context ctx: the context from which the command was made.
        :param Union[Member, Role] mentionable:
        :param str old_reminder_time:
        :param Optional[str] new_reminder_time:
        :param Optional[str] new_message:

        """
        current_guild_id = ctx.guild.id
        old_datetime: datetime = await self.handle_time(old_reminder_time)
        reminder_channel_id: Union[int, None] = Guild.get_reminder_channel_by(current_guild_id)
        current_channel: TextChannel = self.bot.get_channel(reminder_channel_id) or ctx.message.channel
        if Reminder.has_reminder_with(current_guild_id, mentionable.mention, old_datetime):
            new_datetime: datetime = await self.handle_time(new_reminder_time)
            Reminder.update_reminder_with(
                current_guild_id, mentionable.mention, old_datetime, new_datetime, new_message
            )
            await current_channel.send(StaticText.REVISED_REMINDER_NOTIFICATION)
        else:
            raise MissingReminder

    @commands.command(description=HelpDescription.FORGET)
    async def forget(self, ctx: commands.Context, mentionable: Union[Member, Role], reminder_time: str) -> None:
        """
        ...

        :param commands.Context ctx: the context from which the command was made.
        :param Union[Member, Role] mentionable:
        :param str reminder_time:
        """
        mention: str = mentionable.mention
        current_guild_id = ctx.guild.id
        reminder_channel_id: Union[int, None] = Guild.get_reminder_channel_by(current_guild_id)
        current_channel: TextChannel = self.bot.get_channel(reminder_channel_id) or ctx.message.channel
        validated_datetime: datetime = await self.handle_time(reminder_time)
        if Reminder.has_reminder_with(current_guild_id, mention, validated_datetime):
            Reminder.delete_reminder_with(current_guild_id, mention, validated_datetime)
            await current_channel.send(StaticText.FORGOTTEN_REMINDER_NOTIFICATION)
        else:
            raise MissingReminder

    async def handle_time(self, reminder_time: str) -> datetime:
        """
        ...

        :param str reminder_time:
        :return datetime:
        """
        additional_validators: tuple = (self.validate_future_datetime,)
        temporal_defaults: dict = {"default_hour": None, "default_minute": 0}
        validated_datetime: datetime = await self.process_temporality(
            reminder_time, self.parse_datetime, self.validate_datetime,
            additional_validators=additional_validators, default_generator=self.generate_dt_defaults_from_tz,
            manual_defaults=temporal_defaults
        )
        return validated_datetime

    @remind.error
    @revise.error
    @forget.error
    async def reminder_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        This method handles errors exclusive to the reminder Command.

        :param commands.Context ctx: the context from which the command was made.
        :param Exception error: the error raised by some method called to fulfill a reminder request.
        """
        command_name: str = getattr(ctx.command.root_parent, "name", ctx.command.name).title()
        error = getattr(error, "original", error)
        error_name: str = await self.compose_error_name(error.__class__.__name__)
        error_description: Union[str, None] = None
        if isinstance(error, DataError):
            error_description = f'The provided reminder is too long. Please limit your reminder to ' \
                                f'{DiscordConstant.MAX_EMBED_FIELD_VALUE} characters.'
        elif isinstance(error, MissingReminder):
            error_description = 'Your server does not have a reminder scheduled for that time and mention.'
        elif not isinstance(error, DiscordException):
            error_description = f'The error is a non-Discord error. It has the following message: {error}. ' \
                                f'It should be added and handled properly as soon as possible.'
        if error_description:
            error_embed: Embed = await self.initialize_error_embed(command_name, error_name, error_description)
            await ctx.send(embed=error_embed)

    @tasks.loop(minutes=1)
    async def check_reminders(self) -> None:
        """
        ...
        """
        current_time: datetime = datetime.now().replace(microsecond=0)
        current_reminders: list = Reminder.pop_reminders_at(current_time)
        for reminder in current_reminders:
            await self.on_reminder(reminder.guild_id, reminder.mentionable, reminder.reminder_text)

    @check_reminders.before_loop
    async def before_checking_reminders(self) -> None:
        """
        ...
        """
        await self.bot.wait_until_ready()

    async def on_reminder(self, guild_id: int, mention: str, message: str) -> None:
        """
        ...
        :param int guild_id:
        :param str mention:
        :param str message:
        """
        reminder_channel = self.bot.get_channel(Guild.get_reminder_channel_by(guild_id))
        await reminder_channel.send(f"Reminder for {mention}: {message}")
