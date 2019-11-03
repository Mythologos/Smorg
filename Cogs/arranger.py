import discord
from discord.ext import commands
from smorgasDB import Guild


class Arranger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(description='This command tells Smorg what channel in which it should perform some task. ' +
                                'It takes a the type of channel (e.g. quotation, reminder), the channel\'s name, ' +
                                'and, if the channel has the same name as other channels, ' +
                                'the number of the instance of the channel as an argument.')
    async def govern(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("The type of channel given is invalid. Please try again.")

    # TODO: there is a lot that is similar between these sub-commands.
    # Is there any way that I can reduce that?
    @govern.command()
    async def quotation(self, ctx, channel_name='', index=1):
        """
        This method allows users to alter the chat in which Smorg embeds its quotes.
        :param ctx: The context from which the request came.
        :param channel_name: The name of the channel which the user wants to designate as Smorg's quotation domain.
        :param index: Given that multiple channels could have the same name,
        this indicates the instance at which the chosen channel appears.
        Smorg assumes that this is derived from counting Discord channels from top to bottom.
        :return: None.
        """
        govern_message = 'Congrats! You have successfully changed where I engrave your greatest sayings.'
        current_guild = ctx.guild
        valid_channels = [channel for channel in current_guild.text_channels if channel.name == channel_name]
        if valid_channels:
            if isinstance(index, int) and len(valid_channels) >= index > 0:
                Guild.update_quotation_channel(current_guild.id, valid_channels[index - 1].id)
            else:
                govern_message = 'Error: the numerical value given is invalid.'
        else:
            govern_message = 'Error: the channel name given was not found.'
        quotation_channel_id = Guild.get_quotation_channel_by(current_guild.id)
        await self.bot.get_channel(quotation_channel_id).send(govern_message)

    @govern.command()
    async def reminder(self, ctx, channel_name='', index=1):
        """
        This method allows users to alter the chat in which Smorg posts its reminders.
        :param ctx: The context from which the request came.
        :param channel_name: The name of the channel which the user wants to designate as Smorg's reminder domain.
        :param index: Given that multiple channels could have the same name,
        this indicates the instance at which the chosen channel appears.
        Smorg assumes that this is derived from counting Discord channels from top to bottom.
        :return: None.
        """
        govern_message = 'Congrats! You have successfully changed where I blare your noisiest pings.'
        current_guild = ctx.guild
        valid_channels = [channel for channel in current_guild.text_channels if channel.name == channel_name]
        if valid_channels:
            if isinstance(index, int) and len(valid_channels) >= index > 0:
                Guild.update_reminder_channel(current_guild.id, valid_channels[index - 1].id)
            else:
                govern_message = 'Error: the numerical value given is invalid.'
        else:
            govern_message = 'Error: the channel name given was not found.'
        reminder_channel_id = Guild.get_reminder_channel_by(current_guild.id)
        await self.bot.get_channel(reminder_channel_id).send(govern_message)

    @govern.command()
    async def gamble(self, ctx, channel_name='', index=1):
        """
        This method allows users to alter the chat in which Smorg posts its public gambles.
        :param ctx: The context from which the request came.
        :param channel_name: The name of the channel which the user wants to designate as Smorg's gamble domain.
        :param index: Given that multiple channels could have the same name,
        this indicates the instance at which the chosen channel appears.
        Smorg assumes that this is derived from counting Discord channels from top to bottom.
        :return: None.
        """
        govern_message = 'Congrats! You have successfully changed where you let the cards and dice fly.'
        current_guild = ctx.guild
        valid_channels = [channel for channel in current_guild.text_channels if channel.name == channel_name]
        if valid_channels:
            if isinstance(index, int) and len(valid_channels) >= index > 0:
                Guild.update_gamble_channel(current_guild.id, valid_channels[index - 1].id)
            else:
                govern_message = 'Error: the numerical value given is invalid.'
        else:
            govern_message = 'Error: the channel name given was not found.'
        reminder_channel_id = Guild.get_gamble_channel_by(current_guild.id)
        await self.bot.get_channel(reminder_channel_id).send(govern_message)
