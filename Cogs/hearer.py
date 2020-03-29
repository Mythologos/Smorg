# TODO: documentation

import discord
from discord.ext import commands

from smorgasDB import BaseAddition, Guild


class Hearer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reset_database = True

    @commands.Cog.listener()
    async def on_ready(self):
        """
        This method is called Smorg is connected to Discord.
        It assures that it has stored Guild information for every Guild that it is a part of.
        This is important because it must know in which channel it should perform some of its functions.
        :return: None.
        """
        on_ready_message = "Hello! Smorg is online! To view commands, please type '.support'."
        if self.reset_database:
            BaseAddition.reset_database()
        for guild in self.bot.guilds:
            if Guild.exists_with(guild.id):
                channel_id = Guild.get_reminder_channel_by(guild.id)
                # await smorg.get_channel(channel_id).send(on_ready_message)
            else:
                valid_channels = [channel for channel in guild.text_channels if channel.name == 'general']
                if valid_channels:
                    Guild.create_guild_with(guild.id, valid_channels[0].id)
                    # await smorg.get_channel(valid_channels[0].id).send(on_ready_message)
                elif len(guild.text_channels) > 0:
                    Guild.create_guild_with(guild.id, guild.text_channels[0].id)
                    # await smorg.get_channel(guild.text_channels[0].id).send(on_ready_message)
                else:
                    # TODO: make the below better...
                    print("Error! There are no text channels.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: discord.DiscordException):
        """
        TODO -- document!
        :param ctx:
        :param error:
        :return:
        """
        if isinstance(error, discord.ext.commands.CommandNotFound):
            pass
        else:
            print(error)
            # TODO: have some kind of logging?
