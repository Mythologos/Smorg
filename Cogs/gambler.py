"""
...
"""

import discord
import re

from copy import deepcopy
from discord.ext import commands
from random import randint
from typing import Pattern, Union

from smorgasDB import Guild
from Cogs.Helpers.condenser import Condenser
from Cogs.Helpers.embedder import Embedder
from Cogs.Helpers.exceptioner import DuplicateOperator, Exceptioner, ImproperFunction, InvalidRecipient, InvalidRoll, \
    MissingParenthesis, InvalidSequence
from Cogs.Helpers.Enumerators.croupier import MatchContent
from Cogs.Helpers.Enumerators.universalist import ColorConstant, DiscordConstant, HelpDescription, MessageConstant, \
    StaticText
from Cogs.Helpers.yard_shunter import YardShunter


class Gambler(commands.Cog, Condenser, Embedder, Exceptioner):
    """
    ...
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.yard_shunter = YardShunter()

    @commands.command(description=HelpDescription.ROLL)
    async def roll(self, ctx: commands.Context, roll: str, recipients: commands.Greedy[discord.Member] = None, *,
                   description: Union[str, None] = None) -> None:
        """
        ...
        :param ctx:
        :param roll:
        :param recipients:
        :param description:
        :return:
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
            current_channel: discord.TextChannel = self.bot.get_channel(gamble_channel_id) or ctx.message.channel
            await self.send_roll(ctx, roll, flat_tokens, verbose_dice, roll_result, description, current_channel)

    async def handle_roll(self, roll: str) -> tuple:
        """
        ...
        :param roll:
        :return:
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
        ...
        :param raw_roll:
        :param parsed_roll:
        :return:
        """
        parsed_roll_result: str = "".join([matched_item for match in parsed_roll for matched_item in match])
        return raw_roll == parsed_roll_result

    async def handle_dice(self, die_roll: str) -> tuple:
        """
        ...
        :param die_roll:
        :return:
        """
        parsed_dice: dict = await self.parse_dice(die_roll)
        processed_dice: dict = await self.process_dice(parsed_dice)
        return await self.evaluate_roll(processed_dice)

    async def send_roll(self, ctx: commands.Context, roll: str, flat_tokens: list, verbose_dice: list, roll_result: int,
                        description: str, destination_channel: discord.TextChannel) -> None:
        """
        ...
        :param ctx:
        :param roll:
        :param flat_tokens:
        :param verbose_dice:
        :param roll_result:
        :param description:
        :param destination_channel:
        :return:
        """
        introduction_message: str = f"{ctx.message.author.mention}\n" \
                                    f"Initial Roll: {roll}\n" \
                                    f"Reason: {description}"
        await self.send_condensed_message(destination_channel, introduction_message, DiscordConstant.MAX_MESSAGE_LENGTH)
        if verbose_dice:
            field_items = {"counter": None}
            await self.embed(
                destination_channel, verbose_dice, initialize_embed=self.initialize_dice_embed,
                initialize_field=self.initialize_dice_field, field_items=field_items
            )
        evaluated_roll: str = "".join([str(token) for token in flat_tokens])
        conclusion_message: str = f"Evaluated Roll: {evaluated_roll}\n" \
                                  f"Final Result: {roll_result}"
        await self.send_condensed_message(destination_channel, conclusion_message, DiscordConstant.MAX_MESSAGE_LENGTH)

    @staticmethod
    async def initialize_dice_embed(page_number: int = 1) -> discord.Embed:
        """
        ...
        :param page_number:
        :return:
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
    async def initialize_dice_field(raw_roll: str, unsorted_result: list, sorted_result: list, dice_result: int,
                                    counter: int) -> tuple:
        """
        ...
        :param raw_roll:
        :param unsorted_result:
        :param sorted_result:
        :param dice_result:
        :param counter:
        :return:
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
        ...
        :param raw_roll:
        :return:
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
        ...
        :param raw_dice:
        :return:
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
    async def process_dice(matched_dice) -> dict:
        """
        ...
        :param matched_dice:
        :return:
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

    async def evaluate_roll(self, processed_roll) -> tuple:
        """
        ...
        :param processed_roll:
        :return:
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
        ...
        :param number_of_dice:
        :param die_size:
        :param explosion_sign:
        :return:
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
        ...
        :param roll_list:
        :param drop_sign:
        :param keep_sign:
        :param drop_keep_value:
        :return:
        """
        if drop_sign:
            del roll_list[(len(roll_list) - drop_keep_value):]
        elif keep_sign:
            del roll_list[drop_keep_value:]
        return roll_list

    @staticmethod
    async def analyze_roll(roll_list: list, challenge_sign: str, challenge_value: int) -> int:
        """
        ...
        :param roll_list:
        :param challenge_sign:
        :param challenge_value:
        :return:
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
        ...
        :param ctx:
        :param error:
        :return:
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
