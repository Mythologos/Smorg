# TODO: MODULAR DOCUMENTATION

import discord
import random
import secretbord
import smorgasDB
from smorgasDB import Guild, Quote
from discord.ext import commands

smorg = commands.Bot(command_prefix='.')
smorg.remove_command('help')
reset_database = True


@smorg.event
async def on_ready():
    """
    This method is called Smorg is connected to Discord.
    It assures that it has stored Guild information for every Guild that it is a part of.
    This is important because it must know in which channel it should perform some of its functions.
    :return: None.
    """
    on_ready_message = "Hello! Smorg is online! To view commands, please type '.support'."
    if reset_database:
        smorgasDB.reset_database()
    for guild in smorg.guilds:
        if Guild.has_assigned_channel_by(guild.id):
            channel_id = Guild.get_assigned_channel_by(guild.id)
            await smorg.get_channel(channel_id).send(on_ready_message)
        else:
            valid_channels = [channel for channel in guild.text_channels if channel.name == 'general']
            if valid_channels:
                Guild.create_guild_with(guild.id, valid_channels[0].id)
                await smorg.get_channel(valid_channels[0].id).send(on_ready_message)
            elif len(guild.text_channels) > 0:
                Guild.create_guild_with(guild.id, guild.text_channels[0].id)
                await smorg.get_channel(guild.text_channels[0].id).send(on_ready_message)
            else:
                # TODO: make the below better...
                print("Error! There are no text channels.")


@smorg.command(description='This command embeds a quote. It takes a quote (in quotation marks) ' +
                           'and, optionally, an author as arguments.')
async def quote(ctx, quotation='', author='An Anonymous Intellectual'):
    """
    This method receives a quotation and embeds it in its assigned chat.
    :param ctx: The context from which the quotation came.
    :param quotation: a quote to be embedded (a String).
    :param author: the name of the author of the quote (a String).
    :return: None.
    """
    assigned_channel_id = Guild.get_assigned_channel_by(ctx.message.channel.guild.id)
    current_channel = smorg.get_channel(assigned_channel_id)
    quotation = quotation.strip()
    if quotation:
        quote_response = discord.Embed(title='The Marvelous Brainchild of ' + author + ':',
                                       description=quotation,
                                       color=0x20409A)
        await ctx.message.delete()
    else:
        quote_response = discord.Embed(title='Error (Quote): Invalid Quotation',
                                       description='You didn\'t supply a valid quote.',
                                       color=0xB80000)
    await current_channel.send(embed=quote_response)


@smorg.command(description='This command embeds a quote and stores it for posterity\'s sake. ' +
                           'It takes a quote (in quotation marks) and, optionally, an author as arguments.')
async def sanctify(ctx, quotation='', author='An Unknowable Demigod'):
    """
    This method receives a quotation and embeds it in its assigned chat.
    It also stores this information in the database.
    :param ctx: The context from which the quotation came.
    :param quotation: a quote to be embedded (a String).
    :param author: the name of the author of the quote (a String).
    :return: None.
    """
    current_guild_id = ctx.message.channel.guild.id
    assigned_channel_id = Guild.get_assigned_channel_by(current_guild_id)
    current_channel = smorg.get_channel(assigned_channel_id)
    quotation = quotation.strip()
    if quotation:
        quote_response = discord.Embed(title='The Holiest Opus of ' + author + ':',
                                       description=quotation,
                                       color=0xFDF06F)
        if author == 'An Unknowable Demigod':
            Quote.create_quote_with(current_guild_id, quotation)
        else:
            Quote.create_quote_with(current_guild_id, quotation, author)
        await ctx.message.delete()
    else:
        quote_response = discord.Embed(title='Error (Sanctify): Invalid Quotation',
                                       description='You didn\'t supply a valid quote.',
                                       color=0xB80000)
    await current_channel.send(embed=quote_response)


@smorg.command(description='This command retrieves and displays a random stored quote.')
async def yoink(ctx):
    """
    This method retrieves a random Quote formed by the calling Guild in the database.
    It also lets the user know whether a Quote even exists.
    :param ctx: The context from which the quotation came.
    :return: None.
    """
    current_guild_id = ctx.message.channel.guild.id
    maximum = Quote.count_quotes(current_guild_id) - 1
    if maximum >= 0:
        yoinked_quote = Quote.get_random_quote_by(current_guild_id, random.randint(0, maximum))
        author = yoinked_quote[0]
        if not author:
            author = 'A Forgotten Prodigy'
        yoink_response = discord.Embed(title='The Legendary Words of ' + author,
                                       description=yoinked_quote[1],
                                       color=0xEE104E)
    else:
        yoink_response = discord.Embed(title='Error (Yoink): Invalid Request',
                                       description='Your server has no quotes.',
                                       color=0xB80000)
    await ctx.send(embed=yoink_response)


@smorg.command(description='This command tells Smorg what channel in which it should embed quotes. ' +
                           'It takes a channel\'s name and, if the channel has the same name as other channels, ' +
                           'the number of the instance of the channel as an argument.')
async def govern(ctx, channel_name='', index=1):
    """
    This method allows users to alter the chat in which Smorg embeds its quotes.
    :param ctx: The context from which the quotation came.
    :param channel_name: The name of the channel which the user wants to designate as Smorg's Quote domain.
    :param index: Given that multiple channels could have the same name,
    this indicates the instance at which the chosen channel appears.
    Smorg assumes that this is derived from counting Discord channels from top to bottom.
    :return: None.
    """
    govern_message = 'Congrats! You have successfully changed where I engrave your greatest sayings.'
    current_guild = ctx.message.channel.guild
    valid_channels = [channel for channel in current_guild.text_channels if channel.name == channel_name]
    if valid_channels:
        if isinstance(index, int) and len(valid_channels) >= index > 0:
            Guild.update_assigned_channel(current_guild.id, valid_channels[index - 1].id)
        else:
            govern_message = 'Error: the numerical value given is invalid.'
    else:
        govern_message = 'Error: the channel name given was not found.'
    assigned_channel_id = Guild.get_assigned_channel_by(current_guild.id)
    await smorg.get_channel(assigned_channel_id).send(govern_message)


@smorg.command(description='This command retrieves the menu below shown here.')
async def support(ctx):
    """
    This method displays Smorg's help menu.
    :param ctx: The context from which the quotation came.
    :return: None.
    """
    support_embed = discord.Embed(title='Smorg Support',
                                  description='This bot supports the following commands:',
                                  color=0x20409A)
    sorted_commands = sorted(smorg.commands, key=lambda smorg_command: smorg_command.name)
    for command in sorted_commands:
        support_embed.add_field(name='.' + command.name, value=command.description, inline=False)
    await ctx.send(embed=support_embed)

smorg.run(secretbord.bot_key)
