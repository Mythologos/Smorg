import discord
from discord.ext import commands
from smorgasDB import Guild
from random import randint
from copy import deepcopy
import re


class Gambler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='')
    async def chance(self, ctx, roll, description='To Contend with Lady Luck'):
        gamble_channel_id: int = Guild.get_gamble_channel_by(ctx.guild.id)
        current_channel = self.bot.get_channel(gamble_channel_id) if self.bot.get_channel(gamble_channel_id) \
            else ctx.message.channel.id
        roll: str = roll.strip()
        description: str = description.strip()
        roll_parse_result: list = self.parse_roll(roll)
        result_errors: str = ''
        for result in roll_parse_result:
            if isinstance(roll_parse_result, str):
                result_errors = result_errors + result + "\n"
        if result_errors:
            await ctx.send(result_errors)
        else:
            roll_result: tuple = self.evaluate_roll(roll_parse_result)

            raw_result_message: str = self.format_roll_result(roll_result[1])
            end_result_message: str = self.format_roll_result(roll_result[2])
            chance_message = ctx.message.author.mention + "\n" + \
                "Roll: " + roll + "\n" + \
                "Reason: " + description + "\n" + \
                "Raw Result: " + "(" + raw_result_message + ")" + "\n" + \
                "End Result: " + "(" + end_result_message + ")" + " = " + roll_result[0]
            await self.bot.get_channel(current_channel).send(chance_message)

    @commands.command(description='')
    async def hazard(self, ctx, roll, recipient, description):
        ...
        await ...

    def parse_roll(self, roll: str) -> list:
        roll_regex = re.compile('(\d+)[dD](\d+)([dkDK][\d]+)?([+-]\d+)?')
        regex_result = roll_regex.match(roll)
        roll_components: list = []
        roll_list: list = []
        try:
            assert regex_result
            for i in range(1, len(regex_result.groups())):
                roll_components.append(regex_result.group(i))
        except AssertionError:
            roll_list.append("Error: the syntax for the roll was invalid. ")
        else:
            number_rolls_error_message: str = "Error: The quantity given for the number of rolls was not valid. " + \
                                              "Please try again. "
            number_rolls = self.check_basic_roll_component(1, roll_components[0], number_rolls_error_message)
            roll_list.append(number_rolls)

            die_size_error_message: str = "The quantity given for the size of rolls was not valid. Please try again."
            die_size = self.check_basic_roll_component(6, roll_components[1], die_size_error_message)
            roll_list.append(die_size)

            die_size_error_message: str = "Error: The quantity given for the drop or keep roll number was not valid. " + \
                                          "Please try again. "
            die_count_modifier = self.check_basic_roll_component(0, roll_components[2], die_size_error_message)
            if isinstance(die_count_modifier, int) and die_count_modifier < number_rolls:
                if roll_components[2][0:1] in ['d', 'D']:
                    die_count_modifier -= number_rolls
            else:
                die_count_modifier = die_size_error_message
            roll_list.append(die_count_modifier)

            die_roll_mod_error_message: str = "Error: The quantity given for the roll modifier was not valid. " + \
                                              "Please try again. "
            die_roll_modifier = self.check_basic_roll_component(0, roll_components[3], die_roll_mod_error_message)
            if isinstance(die_roll_modifier, int) and roll_components[3][0:1] == '-':
                die_roll_modifier *= -1
            roll_list.append(die_roll_modifier)

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
            roll_result += result

        roll_evaluation: tuple = (roll_result, unsorted_results, individual_results)
        return roll_evaluation

    @staticmethod
    def format_roll_result(roll_sequence):
        result_message: str = ''
        for result in roll_sequence:
            if result_message:
                result_message = ' + ' + str(result)
            else:
                result_message = str(result)
        return result_message

    @staticmethod
    def check_basic_roll_component(default_quantity, item, error_message):
        roll_component_value: int = default_quantity
        try:
            assert item.isalnum()
            roll_component_value = int(item)
        except AssertionError:
            roll_component_value = error_message
        finally:
            return roll_component_value

    # Add explosions later?
    # Add deck of cards?
