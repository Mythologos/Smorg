# TODO: overall documentation

import discord
from discord.ext import commands
from smorgasDB import Guild
from .Helpers.disambiguator import Disambiguator
from random import randint
from copy import deepcopy
from collections import namedtuple
from aenum import Enum
import re


# TODO: move these to a helper class, or separate ones
class RollComponent(Enum):
    NUMBER_OF_DICE = 0
    DIE_SIZE = 1
    DROP_KEEP_VALUE = 2
    EXPLOSION_VALUE = 3
    OVERALL_MODIFIER = 4
    CHALLENGE_VALUE = 5


class RollParseResult(Enum):
    NUMBER_OF_DICE = 0
    DIE_SIZE = 1
    DROP_KEEP_VALUE = 2
    DROP_KEEP_BOOLEAN = 3
    EXPLOSION_BOOLEAN = 4
    OVERALL_MODIFIER = 5
    CHALLENGE_VALUE = 6
    CHALLENGE_INDICATOR = 7


class RollResult(Enum):
    FINAL_RESULT = 0
    UNSORTED_RESULTS = 1
    INDIVIDUAL_RESULTS = 2


# Note: challenge dice systems use > and < but mean >= and <= generally,
# So I use the below in that way.
class ComparisonIndicator(Enum):
    LESS_THAN = -1
    NO_COMPARISON = 0
    GREATER_THAN = 1


class Gambler(commands.Cog, Disambiguator):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='This command gets Smorg to roll one die or multiple dice. ' +
                                  'It currently can handle rolls of the form xdy(k/d)z(!)(+/-)a(>/<)b, '
                                  'where x, y, z, and b are nonnegative integers, ' +
                                  'and where a is an integer. Regular dice, drop-keep syntax, ' +
                                  'exploding dice, challenge dice, and combinations of these are all supported. ' +
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
                                  'It currently can handle rolls of the form xdy(k/d)z(!)(+/-)a(>/<)b, '
                                  'where x, y, z, and b are nonnegative integers, ' +
                                  'and where a is an integer. Regular dice, drop-keep syntax, ' +
                                  'exploding dice, challenge dice, and combinations of these are all supported. ' +
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
            raw_result_message: str = self.format_roll_result(roll_result[RollResult.UNSORTED_RESULTS.value])
            end_result_message: str = self.format_roll_result(roll_result[RollResult.INDIVIDUAL_RESULTS.value])
            modifier_message: str = " + " + str(roll_parse_result[RollParseResult.OVERALL_MODIFIER.value]) \
                if roll_parse_result[RollParseResult.OVERALL_MODIFIER.value] != 0 else ""
            chance_message = ctx.message.author.mention + "\n" + \
                "Roll: " + roll + "\n" + \
                "Reason: " + description + "\n" + \
                "Raw Result: " + "(" + raw_result_message + ")" + modifier_message + "\n" + \
                "End Result: " + "(" + end_result_message + ")" + modifier_message + \
                " = " + str(roll_result[RollResult.FINAL_RESULT.value])
            if roll_parse_result[RollParseResult.CHALLENGE_INDICATOR.value]:
                chance_message += " Successes"
            await destination_channel.send(chance_message)

    def parse_roll(self, roll: str) -> list:
        roll_regex = re.compile('(\d*)[dD](\d*)([dkDK][\d]+)?([!])?([+-]\d+)?([><]\d+)?')
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
            number_rolls = self.check_basic_roll_component(1, roll_components[RollComponent.NUMBER_OF_DICE.value])
            roll_list.append(number_rolls)
            die_size = self.check_basic_roll_component(6, roll_components[RollComponent.DIE_SIZE.value])
            roll_list.append(die_size)

            die_size_error_message: str = "Error: The quantity given for the drop or keep roll number " + \
                                          "was not valid. Please try again."
            die_count_modifier = \
                self.check_basic_roll_component(number_rolls,
                                                roll_components[RollComponent.DROP_KEEP_VALUE.value], 1)
            if roll_components[RollComponent.DROP_KEEP_VALUE.value] and die_count_modifier <= number_rolls:
                if roll_components[RollComponent.DROP_KEEP_VALUE.value][0:1] in ['d', 'D']:
                    die_count_modifier = number_rolls - die_count_modifier
            elif roll_components[RollComponent.DROP_KEEP_VALUE.value]:
                die_count_modifier = die_size_error_message
            drop_keep_boolean: bool = bool(roll_components[RollComponent.DROP_KEEP_VALUE.value])
            roll_list.append(die_count_modifier)
            roll_list.append(drop_keep_boolean)

            die_explosion: bool = (roll_components[RollComponent.
                                   EXPLOSION_VALUE.value] == '!')
            roll_list.append(die_explosion)

            die_roll_modifier = self.check_basic_roll_component(0, roll_components[RollComponent.
                                                                OVERALL_MODIFIER.value], 1)
            if roll_components[RollComponent.OVERALL_MODIFIER.value] and \
                    roll_components[RollComponent.OVERALL_MODIFIER.value][0:1] == '-':
                die_roll_modifier *= -1
            roll_list.append(die_roll_modifier)

            die_challenge_value = self.check_basic_roll_component(0, roll_components[RollComponent.
                                                                  CHALLENGE_VALUE.value], 1)
            roll_list.append(die_challenge_value)
            if roll_components[RollComponent.CHALLENGE_VALUE.value]:
                if roll_components[RollComponent.CHALLENGE_VALUE.value][0:1] == '>':
                    roll_list.append(1)
                else:
                    roll_list.append(-1)
            else:
                roll_list.append(0)
        finally:
            return roll_list

    @staticmethod
    def evaluate_roll(roll_parse_result):
        individual_results: list = []
        roll_index: int = 0
        explosion_count: int = 0
        while roll_index < roll_parse_result[RollParseResult.NUMBER_OF_DICE.value]:
            individual_results.append(randint(1, roll_parse_result[RollParseResult.DIE_SIZE.value]))
            if roll_parse_result[RollParseResult.EXPLOSION_BOOLEAN.value]:
                if individual_results[-1] != roll_parse_result[RollParseResult.DIE_SIZE.value]:
                    roll_index += 1
                else:
                    explosion_count += 1
            else:
                roll_index += 1

        unsorted_results: list = deepcopy(individual_results)
        individual_results.sort(reverse=True)
        if roll_parse_result[RollParseResult.DROP_KEEP_BOOLEAN.value]:
            del individual_results[roll_parse_result[RollParseResult.DROP_KEEP_VALUE.value]:]
        else:
            del individual_results[(roll_parse_result[RollParseResult.DROP_KEEP_VALUE.value] + explosion_count):]

        roll_result: int = roll_parse_result[RollParseResult.OVERALL_MODIFIER.value]

        if roll_parse_result[RollParseResult.CHALLENGE_INDICATOR.value]:
            if roll_parse_result[RollParseResult.CHALLENGE_INDICATOR.value] == ComparisonIndicator.GREATER_THAN.value:
                for result in individual_results:
                    roll_result += (result >= roll_parse_result[RollParseResult.CHALLENGE_VALUE.value])
            else:
                for result in individual_results:
                    roll_result += (result <= roll_parse_result[RollParseResult.CHALLENGE_VALUE.value])
        else:
            for result in individual_results:
                roll_result += result

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

    # TODO: deck of cards; gmroll dice; n-recipient dice rolls; order of operations in modifiers.
    # TODO: warnings / safeguards against generating a message longer than 2000 characters.
    # TODO: handle case of vs. negative challenge dice.
    # TODO: divide up some of these functions; some are getting decently long.
