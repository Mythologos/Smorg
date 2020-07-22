"""
This module contains the recaller Cog. It revolves around the setting, altering, activating, and deleting of reminders.
Reminders are notifications that Smorg pings some mention with at a specified datetime with an optional message.
It consists of three commands: remind, forget, and revise.
"""

from datetime import datetime
from discord import DiscordException, Embed, Member, Role, TextChannel
from discord.ext import commands, tasks
from sqlalchemy.exc import DataError
from typing import Optional, Union

from .Helpers.chronologist import Chronologist
from .Helpers.exceptioner import Exceptioner, MissingReminder
from .Helpers.Enumerators.universalist import DiscordConstant, HelpDescription, StaticText
from ..smorgasDB import Guild, Reminder


class Recaller(commands.Cog, Chronologist, Exceptioner):
    """
    This class centers around reminders. Pertaining to said reminders are three Command objects:
    remind, revise, and forget. The first creates a reminder based on a mention, a written-out datetime,
    and an optional message. The second revises either a reminder's scheduled time or a reminder's message
    (or both) based on given input. Finally, the third deletes a reminder from the database.
    This class also handles the actual pinging process, running a check every minute to see if a reminder
    should be sent. Once a reminder is sent, it is deleted from the database.
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()
        self.check_reminders.start()

    @commands.command(description=HelpDescription.REMIND)
    async def remind(self, ctx: commands.Context, mentionable: Union[Member, Role], reminder_time: str,
                     message: str = "") -> None:
        """
        This Command allows the user to set a reminder for a specific mentionable at a specified time.
        In response, Smorg will ping the mentionable at that time with an optional message.

        :param commands.Context ctx: the context from which the command was made.
        :param Union[Member, Role] mentionable: the mentionable item to which a reminder is to be sent.
        :param str reminder_time: the raw time at which a reminder is to be sent. It should be of the format:
        "HH:MM PP TZ; DD MONTH YY", where all components but the hour are optional and defaults,
        barring the minute being 0 and the time zone being UTC, are based on the given time zone.
        :param str message: additional text to provide a reminder with context.
        """
        current_guild_id = ctx.guild.id
        validated_datetime: datetime = await self.handle_time(reminder_time)
        Reminder.create_reminder_with(current_guild_id, mentionable.mention, message, validated_datetime)
        reminder_channel_id: Union[int, None] = Guild.get_reminder_channel_by(current_guild_id)
        current_channel: TextChannel = self.bot.get_channel(reminder_channel_id) or ctx.channel
        await current_channel.send(StaticText.REMINDER_NOTIFICATION)

    @commands.command(description=HelpDescription.REVISE)
    async def revise(self, ctx: commands.Context, mentionable: Union[Member, Role], old_reminder_time: str,
                     new_reminder_time: Optional[str] = None, new_message: Optional[str] = None) -> None:
        """
        This Command allows the user to revise a reminder already in place.
        The user may do so by first specifying the reminder with its mentionable and scheduled time.
        They then may also add either a new reminder time, a new optional message, or both.

        :param commands.Context ctx: the context from which the command was made.
        :param Union[Member, Role] mentionable: the mentionable item to which a reminder is to be sent.
        :param str old_reminder_time: the old raw time at which a reminder is to be sent. It should be of the format:
        "HH:MM PP TZ; DD MONTH YY", where all components but the hour are optional and defaults,
        barring the minute being 0 and the time zone being UTC, are based on the given time zone.
        :param Optional[str] new_reminder_time: the new raw time at which a reminder is to be sent.
        It should be of the format: "HH:MM PP TZ; DD MONTH YY", where all components but the hour are optional
        and defaults, barring the minute being 0 and the time zone being UTC, are based on the given time zone.
        :param Optional[str] new_message: new, replacement text to provide a reminder with context.
        """
        current_guild_id = ctx.guild.id
        old_datetime: datetime = await self.handle_time(old_reminder_time)
        reminder_channel_id: Union[int, None] = Guild.get_reminder_channel_by(current_guild_id)
        current_channel: TextChannel = self.bot.get_channel(reminder_channel_id) or ctx.channel
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
        This Command allows the user to delete a reminder. To do so, they must specify the reminder
        with its mentionable and scheduled time.

        :param commands.Context ctx: the context from which the command was made.
        :param Union[Member, Role] mentionable: the mentionable item to which a reminder is to be sent.
        :param str reminder_time: the raw time at which a reminder is to be sent. It should be of the format:
        "HH:MM PP TZ; DD MONTH YY", where all components but the hour are optional and defaults,
        barring the minute being 0 and the time zone being UTC, are based on the given time zone.
        """
        mention: str = mentionable.mention
        current_guild_id = ctx.guild.id
        reminder_channel_id: Union[int, None] = Guild.get_reminder_channel_by(current_guild_id)
        current_channel: TextChannel = self.bot.get_channel(reminder_channel_id) or ctx.channel
        validated_datetime: datetime = await self.handle_time(reminder_time)
        if Reminder.has_reminder_with(current_guild_id, mention, validated_datetime):
            Reminder.delete_reminder_with(current_guild_id, mention, validated_datetime)
            await current_channel.send(StaticText.FORGOTTEN_REMINDER_NOTIFICATION)
        else:
            raise MissingReminder

    async def handle_time(self, reminder_time: str) -> datetime:
        """
        This method takes a raw string time and converts it into a valid datetime object;
        it also assures that this datetime will be in the future such that it is valid for use as a reminder's
        scheduled time. It uses Chronologist intensively to handle this.

        :param str reminder_time: the raw time at which a reminder is to be sent. It should be of the format:
        "HH:MM PP TZ; DD MONTH YY", where all components but the hour are optional and defaults,
        barring the minute being 0 and the time zone being UTC, are based on the given time zone.
        :return datetime: the time zone aware date and time at which a reminder will be sent,
        already validated to assure that it is a valid time and in the future.
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
        This method checks to see whether a reminder is ready to be sent using the database method
        pop_reminders_at(). For every reminder that that method returns, this method uses the on_reminder() method
        to send the reminder to the appropriate Guild.
        """
        current_time: datetime = datetime.now().replace(microsecond=0)
        current_reminders: list = Reminder.pop_reminders_at(current_time)
        for reminder in current_reminders:
            await self.on_reminder(reminder.guild_id, reminder.mentionable, reminder.reminder_text)

    @check_reminders.before_loop
    async def before_checking_reminders(self) -> None:
        """
        This method assures that the bot is actually ready before checking to see whether there are any reminders
        to be sent. It's a safeguard to prevent passed but non-deleted reminders from being sent,
        should they linger in the database for some reason.
        """
        await self.bot.wait_until_ready()

    async def on_reminder(self, guild_id: int, mention: str, message: str) -> None:
        """
        This method sends a reminder to a designated channel for a certain Guild.

        :param int guild_id: the ID of the Guild to which the mention and message belong.
        :param str mention: the characters representing a ping for the one whom the reminder is for.
        :param str message: additional text to provide a reminder with context.
        """
        reminder_channel = self.bot.get_channel(Guild.get_reminder_channel_by(guild_id))
        await reminder_channel.send(f"Reminder for {mention}: {message}")
