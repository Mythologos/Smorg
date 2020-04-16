# TODO: documentation

import discord
from discord.ext import commands

from smorgasDB import BaseAddition, Guild


class Hearer(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.reset_database_on_start = True

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This method is called Smorg is connected to Discord.
        It assures that it has stored Guild information for every Guild that it is a part of.
        This is important because it must know in which channel it should perform some of its functions.
        :return: None.
        """
        if self.reset_database_on_start:
            BaseAddition.reset_database()
        for guild in self.bot.guilds:
            if Guild.exists_with(guild.id):
                channel_id: int = Guild.get_reminder_channel_by(guild.id)
                ready_channel: discord.TextChannel = self.bot.get_channel(channel_id)
            else:
                general_channels = [channel for channel in guild.text_channels if channel.name == 'general']
                if general_channels:
                    default_channel_id: int = general_channels[0].id
                elif len(guild.text_channels) > 0:
                    default_channel_id = guild.text_channels[0].id
                else:
                    raise ...  # TODO raise actual error: no text channels
                Guild.create_guild_with(guild.id, default_channel_id)
                ready_channel = self.bot.get_channel(default_channel_id)
            await ready_channel.send(
                "Hello! Smorg is online! To view commands, please type the 'help' command with the appropriate prefix. "
                "If this is your first time using this bot, '.' is your prefix."
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: discord.DiscordException):
        if not isinstance(error, discord.ext.commands.CommandNotFound):
            print(error)
            # TODO: have some kind of logging?
