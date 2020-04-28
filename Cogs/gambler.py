"""
This module contains the gambler Cog. It is based around the roll Command, which rolls dice with expansive syntax
and displays illustrative results.
"""

import discord
import re

from copy import deepcopy
from discord.ext import commands
from random import randint
from typing import Pattern, Union

from Cogs.Helpers.condenser import Condenser
from Cogs.Helpers.embedder import Embedder
from Cogs.Helpers.exceptioner import DuplicateOperator, Exceptioner, ImproperFunction, InvalidRecipient, InvalidRoll, \
    MissingParenthesis, InvalidSequence
from Cogs.Helpers.yard_shunter import YardShunter
from Cogs.Helpers.Enumerators.croupier import MatchContent
from Cogs.Helpers.Enumerators.universalist import ColorConstant, DiscordConstant, HelpDescription, MessageConstant, \
    StaticText
from smorgasDB import Guild


class Gambler(commands.Cog, Condenser, Embedder, Exceptioner):
    """
    This class is centered around the roll command and, with the help of the YardShunter class (and many others),
    calculates and displays a variety of results to a die roll. It frequently has functions that break down
    into handling the whole roll and individual die rolls, as rolls can contain multiple dice and dice
    require individualized handling.
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.yard_shunter = YardShunter()

    @commands.command(description=HelpDescription.ROLL)
    async def roll(self, ctx: commands.Context, roll: str, recipients: commands.Greedy[discord.Member] = None, *,
                   description: Union[str, None] = None) -> None:
        """
        This command performs a die roll, sends it either to the assigned gamble channel, the channel where the die
        was rolled, or certain recipient DM channels, and describes the roll alongside an optional description.

        :param commands.Context ctx: the context from which the command was made.
        :param str roll: the actual roll that is to be performed.
        :param commands.Greedy[discord.Member] recipients: some number of recipients to the roll, each of whom will be
        directly messaged with the roll's results; this does not include the roll's author automatically.
        :param Union[str, None] description: a description of the roll's purpose, if desired.
        """
        flat_tokens, verbose_dice, roll_result = await self.handle_roll(roll)
        if recipients:
            for recipient in recipients:
                if not recipient.dm_channel:
                    await self.bot.get_user(recipient.id).create_dm()
                await self.send_roll(
                    ctx, roll, flat_tokens, verbose_dice, roll_result, description, recipient.dm_channel
                )
        else:
            gamble_channel_id: int = Guild.get_gamble_channel_by(ctx.guild.id)
            current_channel: discord.TextChannel = self.bot.get_channel(gamble_channel_id) or ctx.channel
            await self.send_roll(ctx, roll, flat_tokens, verbose_dice, roll_result, description, current_channel)

    async def handle_roll(self, roll: str) -> tuple:
        """
        This method parses a roll, assures its validity, rolls dice if they exist, and calculates
        the overall roll result.

        :param str roll: the actual roll that is to be performed.
        :return tuple: a list of all items matched from roll, a tuple of the full results of each die roll,
        and a float or integer that represents the final result of the roll.
        """
        raw_roll: str = roll.replace(' ', '')
        parsed_roll: list = await self.parse_roll(raw_roll)
        roll_is_valid: bool = await self.is_roll_valid(raw_roll, parsed_roll)
        if not roll_is_valid:
            raise InvalidRoll
        else:
            verbose_dice: list = []
            for match_index, match in enumerate(parsed_roll):
                die_roll: str = match[MatchContent.DIE_ROLL]
                if die_roll:
                    dice_result, unsorted_results, sorted_results = await self.handle_dice(die_roll)
                    verbose_dice.append((die_roll, unsorted_results, sorted_results, dice_result))
                    parsed_roll[match_index] = (str(dice_result),)
            flat_matches: list = [item for match in parsed_roll for item in match if item]
            roll_result = await self.yard_shunter.shunt_yard(flat_matches)
            return flat_matches, verbose_dice, roll_result

    @staticmethod
    async def is_roll_valid(raw_roll: str, parsed_roll: list) -> bool:
        """
        This method determines whether all items from the original roll were kept in the parsing.
        If not, the roll is deemed to be invalid and False is returned.

        :param str raw_roll: the actual roll that is to be performed with spaces removed.
        :param str parsed_roll: the roll having been parsed by the parse_roll() function.
        :return bool: True if raw_roll and a concatenation of all matches in parsed_roll are the same; otherwise, False.
        """
        parsed_roll_result: str = "".join([matched_item for match in parsed_roll for matched_item in match])
        return raw_roll == parsed_roll_result

    async def handle_dice(self, die_roll: str) -> tuple:
        """
        This method evaluates dice rolls, parsing them and subsequently processing them to return
        information on the summed result, the unsorted individual results of each die,
        and the sorted result of each die.

        :param str die_roll: a die roll having been parsed out by the parse_roll() method.
        :return tuple: the result of evaluate_dice(), which is a collection of three different pieces of information
        about a roll--the unsorted die rolls, the sorted die rolls, and the sum of the die results.
        """
        parsed_dice: dict = await self.parse_dice(die_roll)
        processed_dice: dict = await self.process_dice(parsed_dice)
        return await self.evaluate_dice(processed_dice)

    async def send_roll(self, ctx: commands.Context, roll: str, flat_tokens: list, verbose_dice: list, roll_result: int,
                        description: Union[str, None], destination_channel: discord.TextChannel) -> None:
        """
        This method sends detailed roll results to a target channel. All relevant information is determined before
        this method is used; this method only handles the formatting and disclosure of such information.
        It employs Embedder and Condenser to do so.

        :param commands.Context ctx: the context from which the command was made.
        :param str roll: the actual roll that is to be performed.
        :param list flat_tokens: the roll that was evaluated with die rolls exchanged for their summed results.
        :param list verbose_dice: a collection of tuples that contain varying information on a die roll,
        including unsorted results, sorted results, and the summed dice result.
        :param int roll_result: the final result of the roll.
        :param Union[str, None] description: a description of the roll's purpose, if desired.
        :param discord.TextChannel destination_channel: the location where the roll results will be outputted.
        """
        introduction_message: str = f"{ctx.author.mention}\n" \
                                    f"Initial Roll: {roll}\n" \
                                    f"Reason: {description}"
        await self.send_condensed_message(destination_channel, introduction_message, DiscordConstant.MAX_MESSAGE_LENGTH)
        if verbose_dice:
            field_items = {"counter": None}
            await self.embed(
                destination_channel, verbose_dice, initialize_embed=self.initialize_roll_embed,
                initialize_field=self.initialize_roll_field, field_items=field_items
            )
        evaluated_roll: str = "".join([str(token) for token in flat_tokens])
        conclusion_message: str = f"Evaluated Roll: {evaluated_roll}\n" \
                                  f"Final Result: {roll_result}"
        await self.send_condensed_message(destination_channel, conclusion_message, DiscordConstant.MAX_MESSAGE_LENGTH)

    @staticmethod
    async def initialize_roll_embed(page_number: int = 1) -> discord.Embed:
        """
        This method creates a Discord Embed that dice roll results.

        :param int page_number: the number indicating that the nth Embed is being created.
        :return discord.Embed: an Embed used to store and to output information on dice roll results.
        """
        if page_number == 1:
            desc: str = "The results of the individual dice roll(s) are as follows:"
        else:
            desc = "Further rolls resulted in the following ways:"
        dice_embed: discord.Embed = discord.Embed(
            title=f"Individual Dice Results, Page {page_number}",
            description=desc,
            color=ColorConstant.NEUTRAL_ORANGE
        )
        return dice_embed

    @staticmethod
    async def initialize_roll_field(raw_roll: str, unsorted_result: list, sorted_result: list, dice_result: int,
                                    counter: int) -> tuple:
        """
        This method creates the main attributes of a field for an Embed object to display dice result information.
        It truncates fields appropriately to prevent overflow.

        :param str raw_roll: the base dice roll performed.
        :param list unsorted_result: the results of the dice roll, left unsorted.
        :param list sorted_result: the results of the dice roll, sorted.
        :param int dice_result: the summed result of the dice roll.
        :param int counter: a number representing the position of the item in its data structure.
        :return: two strings and a Boolean for the three keyword arguments of an Embed field.
        """
        name: str = f"Dice Roll {counter + 1}: {raw_roll}"
        sum_string: str = str(dice_result)
        sorted_result_string: str = str(sorted_result)
        unsorted_result_string: str = str(unsorted_result)
        safe_field_length: int = (DiscordConstant.MAX_EMBED_FIELD_VALUE -
                                  (MessageConstant.DIE_ROLL_CHARACTERS + MessageConstant.DIE_TRUNCATION_CHARACTERS))
        if (len(sum_string) + len(sorted_result_string)) <= safe_field_length:
            if (len(sum_string) + len(sorted_result_string) + len(unsorted_result_string)) > safe_field_length:
                unsorted_result_string = StaticText.LIST_TRUNCATION_TEXT
        else:
            sorted_result_string = StaticText.LIST_TRUNCATION_TEXT
            unsorted_result_string = StaticText.LIST_TRUNCATION_TEXT
        value: str = f"**Raw Dice Result:** {unsorted_result_string}\n" \
                     f"**Final Dice Result:** {sorted_result_string}\n" \
                     f"**Sum:** {sum_string}"
        inline: bool = False
        return name, value, inline

    @staticmethod
    async def parse_roll(raw_roll: str) -> list:
        """
        This method uses a re.Pattern to parse a roll and outputs all matches as a list of tuples.

        :param str raw_roll: the base dice roll performed.
        :return list: a collection of tuples that contain pattern matches of one of the five groups in roll_pattern.
        """
        roll_pattern: Pattern = re.compile(r'(?:(?P<roll>[\d]+[dD][\d]+(?:[dDkK][\d]+)?(?:!)?(?:[><][+-]?[\d]+)?)|'
                                           r'(?P<regular_operator>[+\-*/^])|'
                                           r'(?P<grouping_operator>[()])|'
                                           r'(?P<function>abs|floor|ceiling|sqrt)|'
                                           r'(?P<constant>[+-]?[\d]+))')
        return re.findall(roll_pattern, raw_roll)

    @staticmethod
    async def parse_dice(raw_dice: str) -> dict:
        """
        This method uses a re.Pattern to parse a dice roll and outputs all segments of a match as a dictionary.

        :param str raw_dice: the base dice being rolled.
        :return dict: a mapping of named portions of the Pattern to the items that they matched in raw_dice
        """
        dice_pattern: Pattern = re.compile(r'(?P<number_of_dice>[\d]+)[dD]'
                                           r'(?P<die_size>[\d]+)'
                                           r'(?P<drop_keep_sign>(?P<drop_sign>[dD])|(?P<keep_sign>[kK]))?'
                                           r'(?(drop_keep_sign)(?P<drop_keep_value>[\d]+))?'
                                           r'(?P<explosion_sign>!)?'
                                           r'(?P<challenge_sign>[><])?'
                                           r'(?(challenge_sign)(?P<challenge_value>[+-]?[\d]+))')
        return re.match(dice_pattern, raw_dice).groupdict()

    @staticmethod
    async def process_dice(matched_dice: dict) -> dict:
        """
        This method extracts important information from dice matched in parse_dice() and
        converts values to types that other functions would find more useful.

        :param dict matched_dice: a dictionary containing the fields outputted by the parse_dice() function.
        :return dict: a dictionary containing a simplification and type-shifting of the fields in matched_dice.
        """
        number_of_dice: int = int(matched_dice['number_of_dice'])
        die_size: int = int(matched_dice['die_size'])
        drop_keep_value: int = int(matched_dice['drop_keep_value']) if matched_dice['drop_keep_value'] else None
        challenge_value: int = int(matched_dice['challenge_value']) if matched_dice['challenge_value'] else None
        return {
            'number_of_dice': number_of_dice,
            'die_size': die_size,
            'drop_sign': matched_dice['drop_sign'],
            'keep_sign': matched_dice['keep_sign'],
            'drop_keep_value': drop_keep_value,
            'explosion_sign': matched_dice['explosion_sign'],
            'challenge_sign': matched_dice['challenge_sign'],
            'challenge_value': challenge_value,
        }

    async def evaluate_dice(self, processed_roll: dict) -> tuple:
        """
        This method evaluates the result of a roll in terms of its individual results and its summed result.
        It does so by using helper methods.

        :param dict processed_roll: a mapping of labeled values put into data types in accordance with process_dice().
        :return tuple: a collection of the dice's summed result, its unsorted individual results,
        and its sorted individual results.
        """
        roll_results: list = await self.roll_dice(
            processed_roll['number_of_dice'], processed_roll['die_size'], processed_roll['explosion_sign']
        )
        unsorted_results: list = deepcopy(roll_results)
        roll_results.sort(reverse=True)
        roll_results = await self.select_dice(
            roll_results, processed_roll['drop_sign'], processed_roll['keep_sign'], processed_roll['drop_keep_value']
        )
        roll_result: int = await self.analyze_roll(
            roll_results, processed_roll['challenge_sign'], processed_roll['challenge_value']
        )
        return roll_result, unsorted_results, roll_results

    @staticmethod
    async def roll_dice(number_of_dice: int, die_size: int, explosion_sign: str) -> list:
        """
        This method actually rolls dice with a random algorithm based on a given dice size, number of dice,
        and an indication of whether or not the dice should explode.

        :param int number_of_dice: the number of dice to be rolled (e.g. the 3 in 3d6).
        :param int die_size: the size of the dice to be rolled (e.g. the 6 in 3d6).
        :param str explosion_sign: a designation of whether dice explode (i.e. an extra die is added when
        a die results in the maximum amount for its size).
        :return list: a collection of the individual results of the roll.
        """
        roll_list: list = []
        roll_index: int = 0
        while roll_index < number_of_dice:
            single_roll = randint(1, die_size)
            roll_list.append(single_roll)
            if not (explosion_sign and single_roll == die_size):
                roll_index += 1
        return roll_list

    @staticmethod
    async def select_dice(roll_list: list, drop_sign: str, keep_sign: str, drop_keep_value: int) -> list:
        """
        This method truncates dice depending upon the values of drop_sign and keep_sign.
        A die can only use drop or keep and not both; moreover, each of these signs play by different rules.
        Drop removes the lowest values from roll_list, whereas keep only keeps a certain number of values.
        This difference comes into play when an effect causes the number of dice to change, such as an explosion.

        :param list roll_list: a sorted list of die results.
        :param str drop_sign: an indication of whether the drop behavior should be used.
        :param str keep_sign: an indication of whether the keep behavior should be used.
        :param int drop_keep_value: the number of dice that should be dropped or kept.
        :return: a list of sorted die results with the designated drop-keep behavior applied to it.
        """
        if drop_sign:
            del roll_list[(len(roll_list) - drop_keep_value):]
        elif keep_sign:
            del roll_list[drop_keep_value:]
        return roll_list

    @staticmethod
    async def analyze_roll(roll_list: list, challenge_sign: str, challenge_value: int) -> int:
        """
        This method sums a roll based on one of two rule sets.
        First, it could sum them normally and output the result.
        Second, if a challenge_sign and challenge_value exist, then the number of individual die rolls meeting or
        exceeding challenge_value is counted and returned.

        :param list roll_list: a collection of die roll results.
        :param str challenge_sign: an indication of whether challenge die behavior should be used.
        :param int challenge_value: the value which dice must meet or exceed to be counted as a success
        in challenge die behavior.
        :return int: the summed result of the dice in accordance with the designated rule set.
        """
        roll_result: int = 0
        if challenge_sign:
            if challenge_sign == '>':
                for result in roll_list:
                    roll_result += (result >= challenge_value)
            elif challenge_sign == '<':
                for result in roll_list:
                    roll_result += (result <= challenge_value)
        else:
            for roll in roll_list:
                roll_result += roll
        return roll_result

    @roll.error
    async def roll_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        This method handles errors exclusive to the roll Command.

        :param commands.Context ctx: the context from which the command was made
        :param Exception error: the error raised by some method called to fulfill a roll request
        """
        command_name: str = getattr(ctx.command.root_parent, "name", ctx.command.name).title()
        error = getattr(error, "original", error)
        error_name: str = await self.compose_error_name(error.__class__.__name__)
        error_description: Union[str, None] = None
        if isinstance(error, DuplicateOperator):
            error_description = 'The roll contains a duplicate operator.'
        elif isinstance(error, ImproperFunction):
            error_description = 'A function in your roll is missing a starting parenthesis.'
        elif isinstance(error, InvalidRecipient):
            error_description = f'No individual matches the recipient name {error}.'
        elif isinstance(error, MissingParenthesis):
            error_description = 'Your roll has imbalanced parentheses.'
        elif isinstance(error, InvalidRoll):
            error_description = 'Your roll contains invalid characters or sequences of characters.'
        elif isinstance(error, InvalidSequence):
            error_description = 'Your roll does not contain the right amount of operands ' \
                                'for your operators or functions.'
        elif not isinstance(error, discord.DiscordException):
            error_description = f'The error is a non-Discord error. It has the following message: {error}. ' \
                                f'It should be added and handled properly as soon as possible.'
        if error_description:
            error_embed = await self.initialize_error_embed(command_name, error_name, error_description)
            await ctx.send(embed=error_embed)
