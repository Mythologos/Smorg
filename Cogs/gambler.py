# TODO: overall documentation
# TODO: deck of cards.

# Current Agenda:
# TODO: warnings / safeguards against generating a message longer than 2000 characters.
# TODO: exceptions for incorrect roll syntax.
# TODO: divide up some of these functions; some are getting decently long.

import discord
import asyncio
import re

from copy import deepcopy
from discord.ext import commands
from random import randint
from typing import Match

from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator
from Cogs.Helpers.exceptioner import DuplicateOperator, ImproperFunction, InvalidRecipient, MissingParenthesis
from Cogs.Helpers.Enumerators.croupier import MatchContents
from Cogs.Helpers.Enumerators.universalist import ColorConstants, DiscordConstants, HelpDescriptions
from Cogs.Helpers.yard_shunter import YardShunter


class Gambler(commands.Cog, Disambiguator):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.yard_shunter = YardShunter()

    @commands.command(description=HelpDescriptions.ROLL)
    async def roll(self, ctx: commands.Context, roll: str, recipients: commands.Greedy[discord.Member] = None, *,
                   description: str = 'To Contend with Lady Luck') -> None:
        """
        The main method for the roll command.
        :param ctx: The context from which the request came.
        :param roll: The roll which the user gives for the bot to simulate.
        See HelpDescriptions.ROLL for a description of a dice roll's format.
        :param description: A string description of what the roll is meant for.
        :param recipients: A list of names or nicknames of individuals from a Guild that
        the requester wants to which the requester wants to send results.
        :return: None.
        """
        flat_tokens, verbose_dice, roll_result = await self.handle_roll(roll)
        if recipients:
            for recipient in recipients:
                if not recipient.dm_channel:
                    await self.bot.get_user(recipient.id).create_dm()
                await self.send_roll(ctx, roll, flat_tokens, verbose_dice,
                                     roll_result, description, recipient.dm_channel)
        else:
            gamble_channel_id: int = Guild.get_gamble_channel_by(ctx.guild.id)
            current_channel = self.bot.get_channel(gamble_channel_id) if self.bot.get_channel(gamble_channel_id) \
                else ctx.message.channel
            await self.send_roll(ctx, roll, flat_tokens, verbose_dice, roll_result, description, current_channel)

    async def handle_roll(self, roll: str) -> tuple:
        raw_roll: str = roll.replace(' ', '')
        parsed_roll: list = await self.parse_roll(raw_roll)
        verbose_dice: list = []
        for match_index, match in enumerate(parsed_roll):
            die_roll: str = match[MatchContents.DIE_ROLL.value]
            if die_roll:
                parsed_dice: Match = await self.parse_dice(die_roll)
                processed_dice: dict = await self.process_dice(parsed_dice)
                dice_result, unsorted_results, sorted_results = await self.evaluate_roll(processed_dice)
                verbose_dice.append((die_roll, unsorted_results, sorted_results, dice_result))
                parsed_roll[match_index] = (str(dice_result),)
        flat_matches: list = [item for match in parsed_roll for item in match if item]
        roll_result = await self.yard_shunter.shunt_yard(flat_matches)
        return flat_matches, verbose_dice, roll_result

    async def send_roll(self, ctx: commands.Context, roll: str, flat_tokens: list, verbose_dice: list, roll_result: int,
                        description: str, destination_channel: discord.TextChannel):
        description: str = description.strip()
        introductory_message: str = f"{ctx.message.author.mention}\n" \
                                    f"Initial Roll: {roll}\n" \
                                    f"Reason: {description}"
        await destination_channel.send(introductory_message)
        if verbose_dice:
            await self.send_dice(verbose_dice, destination_channel)
        evaluated_roll: str = "".join([str(token) for token in flat_tokens])
        concluding_message = f"The evaluated roll was: {evaluated_roll}\n" \
                             f"The final result of this roll is: {roll_result}"
        await destination_channel.send(concluding_message)

    @staticmethod
    async def send_dice(verbose_dice: list, destination_channel: discord.TextChannel) -> None:
        verbose_roll_embed = discord.Embed(
            title=f"Individual Dice Results",
            description="The results of the individual roll(s) are as follows:",
            color=ColorConstants.NEUTRAL_ORANGE
        )
        for counter, (raw_roll, unsorted_result, sorted_result, dice_result) in enumerate(verbose_dice, 1):
            if counter and (counter % DiscordConstants.MAX_EMBED_FIELDS) == 0:
                await destination_channel.send(embed=verbose_roll_embed)
                verbose_roll_embed = discord.Embed(
                    title=f"Individual Dice Results, Page {(counter // DiscordConstants.MAX_EMBED_FIELDS) + 1}",
                    description="Further individual roll results are as follows:",
                    color=ColorConstants.NEUTRAL_ORANGE
                )
            verbose_roll_embed.add_field(
                name=f"Dice Roll {counter + 1}: {raw_roll}",
                value=f"**Raw Dice Result:** {unsorted_result}\n"
                      f"**Final Dice Result:** {sorted_result}\n"
                      f"**Sum:** {dice_result}",
                inline=False
            )
        await destination_channel.send(embed=verbose_roll_embed)

    @staticmethod
    async def parse_roll(raw_roll: str) -> list:
        roll_pattern = re.compile(r'(?:(?P<roll>[\d]+[dD][\d]+(?:[dDkK][\d]+)?(?:!)?(?:[><][+-]?[\d]+)?)|'
                                  r'(?P<regular_operator>[+\-*/^])|'
                                  r'(?P<grouping_operator>[()])|'
                                  r'(?P<function>abs|floor|ceiling|sqrt)|'
                                  r'(?P<constant>[+-]?[\d]+))')
        return re.findall(roll_pattern, raw_roll)

    @staticmethod
    async def parse_dice(raw_dice: str) -> Match:
        dice_pattern = re.compile(r'(?P<number_of_dice>[\d]+)[dD]'
                                  r'(?P<die_size>[\d]+)'
                                  r'(?P<drop_keep_sign>(?P<drop_sign>[dD])|(?P<keep_sign>[kK]))?'
                                  r'(?(drop_keep_sign)(?P<drop_keep_value>[\d]+))?'
                                  r'(?P<explosion_sign>!)?'
                                  r'(?P<challenge_sign>[><])?'
                                  r'(?(challenge_sign)(?P<challenge_value>[+-]?[\d]+))')
        return re.match(dice_pattern, raw_dice)

    @staticmethod
    async def process_dice(matched_dice) -> dict:
        number_of_dice: int = int(matched_dice.group('number_of_dice'))
        die_size: int = int(matched_dice.group('die_size'))
        drop_keep_value: int = int(matched_dice.group('drop_keep_value')) if matched_dice.group(
            'drop_keep_value') else None
        challenge_value: int = int(matched_dice.group('challenge_value')) if matched_dice.group(
            'challenge_value') else None
        return {
            'number_of_dice': number_of_dice,
            'die_size': die_size,
            'drop_sign': matched_dice.group('drop_sign'),
            'keep_sign': matched_dice.group('keep_sign'),
            'drop_keep_value': drop_keep_value,
            'explosion_sign': matched_dice.group('explosion_sign'),
            'challenge_sign': matched_dice.group('challenge_sign'),
            'challenge_value': challenge_value,
        }

    async def evaluate_roll(self, processed_roll) -> tuple:
        roll_results: list = await self.roll_dice(processed_roll['number_of_dice'], processed_roll['die_size'],
                                                  processed_roll['explosion_sign'])
        unsorted_results: list = deepcopy(roll_results)
        roll_results.sort(reverse=True)
        roll_results = await self.select_dice(roll_results, processed_roll['drop_sign'], processed_roll['keep_sign'],
                                              processed_roll['drop_keep_value'])
        roll_result: int = await self.analyze_roll(roll_results, processed_roll['challenge_sign'],
                                                   processed_roll['challenge_value'])
        return roll_result, unsorted_results, roll_results

    @staticmethod
    async def roll_dice(number_of_dice: int, die_size: int, explosion_sign: str) -> list:
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
        if drop_sign:
            del roll_list[(len(roll_list) - drop_keep_value):]
        elif keep_sign:
            del roll_list[drop_keep_value:]
        return roll_list

    @staticmethod
    async def analyze_roll(roll_list: list, challenge_sign: str, challenge_value: int) -> int:
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
    async def roll_error(self, ctx: commands.Context, error: discord.DiscordException) -> None:
        if isinstance(error, commands.ExpectedClosingQuoteError):
            error_embed = discord.Embed(
                title='Error (Roll): Missing Closing Quote',
                description=f'You forgot to close the quotation on one of your arguments.',
                color=ColorConstants.ERROR_RED
            )
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, DuplicateOperator):
                error_embed = discord.Embed(
                    title='Error (Roll): Duplicate Operator',
                    description=f'The roll contains a duplicate operator.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, ImproperFunction):
                error_embed = discord.Embed(
                    title='Error (Roll): Improper Function',
                    description=f'A function in your roll is missing a starting parenthesis.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, InvalidRecipient):
                error_embed = discord.Embed(
                    title='Error (Roll): Invalid Recipient',
                    description=f'No individual matches the recipient name {error}.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, MissingParenthesis):
                error_embed = discord.Embed(
                    title='Error (Roll): Missing Parenthesis',
                    description=f'Your roll has imbalanced parentheses.',
                    color=ColorConstants.ERROR_RED
                )
            elif isinstance(error, commands.MissingRequiredArgument):
                error_embed = discord.Embed(
                    title='Error (Roll): Missing Required Argument',
                    description=f'You didn\'t supply a roll.',
                    color=ColorConstants.ERROR_RED
                )
            else:
                error_embed = discord.Embed(
                    title='Error (Roll): User Input Error',
                    description=f'The error type is: {error}. A better error message will be supplied soon.',
                    color=ColorConstants.ERROR_RED
                )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, asyncio.TimeoutError):
                error_embed = discord.Embed(
                    title='Error (Roll): Disambiguation Timeout',
                    description='You didn\'t supply a valid integer quickly enough.',
                    color=ColorConstants.ERROR_RED
                )
            else:
                error_embed = discord.Embed(
                    title='Error (Roll): Command Invoke Error',
                    description=f'The error type is: {error}. A better error message will be supplied soon.',
                    color=ColorConstants.ERROR_RED
                )
        else:
            error_embed = discord.Embed(
                title='Error (Roll): Miscellaneous Error',
                description=f'The error type is: {error}. A better error message will be supplied soon.',
                color=ColorConstants.ERROR_RED
            )
        await ctx.send(embed=error_embed)
