# TODO: overall documentation

import discord
from discord.ext import commands
from smorgasDB import Guild
from .Helpers.disambiguator import Disambiguator
from random import randint
from copy import deepcopy
from collections import namedtuple
import re


class Gambler(commands.Cog, Disambiguator):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='This command gets Smorg to roll one die or multiple dice. ' +
                                  'It currently can handle rolls of the form xdy(k/d)z(+/-)a, '
                                  'where x, y, and z are nonnegative numbers, ' +
                                  'where x is the number of dice to be rolled, ' +
                                  'where y is the number of sides on each die, ' +
                                  'where z is the number of dice to keep (k) or drop (d), ' +
                                  'and where a is an overall additive or subtractive modifier. ' +
                                  'Only the the first "d" is required to perform a roll. ' +
                                  'The default x value is 1. The default y value is 6. The others default to 0. ' +
                                  'Quoted, a description of what the roll was for may be included afterward. ' +
                                  'The result is posted either in a set gamble channel or where the die was rolled.')
    async def chance(self, ctx, roll, description='To Contend with Lady Luck'):
        gamble_channel_id: int = Guild.get_gamble_channel_by(ctx.guild.id)
        current_channel = self.bot.get_channel(gamble_channel_id) if self.bot.get_channel(gamble_channel_id) \
            else ctx.message.channel
        await self.handle_roll(ctx, current_channel, roll, description)

    @commands.command(description='This command gets Smorg to blindly roll one die or multiple dice. ' +
                                  'It currently can handle rolls of the form xdy(k/d)z(+/-)a, '
                                  'where x, y, and z are nonnegative numbers, ' +
                                  'where x is the number of dice to be rolled, ' +
                                  'where y is the number of sides on each die, ' +
                                  'where z is the number of dice to keep (k) or drop (d), ' +
                                  'and where a is an overall additive or subtractive modifier. ' +
                                  'and where a is an overall additive or subtractive modifier. ' +
                                  'Only the the first "d" is required to perform a roll. ' +
                                  'The default x value is 1. The default y value is 6. The others default to 0. ' +
                                  'Quoted, a recipient\'s username or Guild nickname ' +
                                  'must be given to DM the roll\'s result only to that person. ' +
                                  'Quoted afterward, a description of what the roll was for may also be included.')
    async def hazard(self, ctx, roll, recipient, description='To Contend with Lady Luck'):
        ReducedMember = namedtuple('ReducedMember', 'nickname username id')
        guild_members: list = list(map(lambda member: ReducedMember(member.nick, member.name, member.id),
                                       ctx.guild.members))
        recipient_options: list = []
        for reduced_member in guild_members:
            if recipient in [reduced_member.nickname, reduced_member.username]:
                recipient_options.append(reduced_member)
        if len(recipient_options) == 0:
            await ctx.send("Error: no individual matches the recipient name or nickname given. Please try again.")
        else:
            chosen_recipient_index: int = await Disambiguator.disambiguate(self.bot, ctx, recipient_options)
            chosen_recipient = self.bot.get_user(recipient_options[chosen_recipient_index].id)
            if not chosen_recipient.dm_channel:
                await self.bot.get_user(chosen_recipient.id).create_dm()
            recipient_dm_channel = chosen_recipient.dm_channel
            await self.handle_roll(ctx, recipient_dm_channel, roll, description)

    async def handle_roll(self, ctx, destination_channel, roll, description):
        roll: str = roll.strip()
        description: str = description.strip()
        roll_parse_result: list = self.parse_roll(roll)
        result_errors: str = ''
        for result in roll_parse_result:
            if isinstance(result, str):
                result_errors = result_errors + result + "\n"
        if result_errors:
            await ctx.send(result_errors)
        else:
            roll_result: tuple = self.evaluate_roll(roll_parse_result)
            raw_result_message: str = self.format_roll_result(roll_result[1])
            end_result_message: str = self.format_roll_result(roll_result[2])
            modifier_message: str = " + " + str(roll_parse_result[3]) if roll_parse_result[3] != 0 else ""
            chance_message = ctx.message.author.mention + "\n" + \
                "Roll: " + roll + "\n" + \
                "Reason: " + description + "\n" + \
                "Raw Result: " + "(" + raw_result_message + ")" + modifier_message + "\n" + \
                "End Result: " + "(" + end_result_message + ")" + modifier_message + \
                " = " + str(roll_result[0])
            await destination_channel.send(chance_message)

    def parse_roll(self, roll: str) -> list:
        roll_regex = re.compile('(\d*)[dD](\d*)([dkDK][\d]+)?([+-]\d+)?')
        regex_result = roll_regex.match(roll)
        roll_components: list = []
        roll_list: list = []
        try:
            assert regex_result
            for i in range(1, 1 + len(regex_result.groups())):
                roll_components.append(regex_result.group(i))
        except AssertionError:
            roll_list.append("Error: the syntax for the roll was invalid.")
        else:
            number_rolls = self.check_basic_roll_component(1, roll_components[0])
            roll_list.append(number_rolls)
            die_size = self.check_basic_roll_component(6, roll_components[1])
            roll_list.append(die_size)

            die_size_error_message: str = "Error: The quantity given for the drop or keep roll number " + \
                                          "was not valid. Please try again."
            die_count_modifier = self.check_basic_roll_component(number_rolls, roll_components[2], 1)
            if roll_components[2] and die_count_modifier <= number_rolls:
                if roll_components[2][0:1] in ['d', 'D']:
                    die_count_modifier -= number_rolls
            elif roll_components[2]:
                die_count_modifier = die_size_error_message
            roll_list.append(die_count_modifier)

            die_roll_modifier = self.check_basic_roll_component(0, roll_components[3], 1)
            if roll_components[3] and roll_components[3][0:1] == '-':
                die_roll_modifier *= -1
            roll_list.append(die_roll_modifier)
        finally:
            return roll_list

    @staticmethod
    def evaluate_roll(roll_parse_result):
        individual_results: list = []
        for i in range(0, roll_parse_result[0]):
            individual_results.append(randint(1, roll_parse_result[1]))
        unsorted_results: list = deepcopy(individual_results)

        individual_results.sort(reverse=True)
        del individual_results[roll_parse_result[2]:]
        roll_result: int = roll_parse_result[3]
        for result in individual_results:
            roll_result = roll_result + result
        roll_evaluation: tuple = (roll_result, unsorted_results, individual_results)
        return roll_evaluation

    @staticmethod
    def format_roll_result(roll_sequence):
        result_message: str = ''
        for result in roll_sequence:
            if result_message:
                result_message = result_message + ' + ' + str(result)
            else:
                result_message = str(result)
        return result_message

    @staticmethod
    def check_basic_roll_component(default_quantity, item, character_range_start=0, character_range_end=None):
        roll_component_value: int = default_quantity
        if item and item[character_range_start:character_range_end].isalnum():
            roll_component_value = int(item[character_range_start:character_range_end])
        return roll_component_value

    # Add explosions later?
    # Add deck of cards?
