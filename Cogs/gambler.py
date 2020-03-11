# TODO: overall documentation
# TODO: deck of cards.

# Current Agenda:
# TODO: warnings / safeguards against generating a message longer than 2000 characters.
# TODO: exceptions for incorrect roll syntax. (e.g.: challenge rolls that end up using characters.)
# TODO: divide up some of these functions; some are getting decently long.
# TODO: allow and pre-remove spaces in roll syntax
# TODO: update roll presentation to be in embeds?

from discord.ext import commands
from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator
from Cogs.Helpers.Enumerators.croupier import MessageConstants
from Cogs.Helpers.yard_shunter import YardShunter
from random import randint
from copy import deepcopy
from collections import namedtuple
import re


class Gambler(commands.Cog, Disambiguator):
    def __init__(self, bot):
        self.bot = bot
        self.yard_shunter = YardShunter()

    @commands.command(description='This command gets Smorg to roll one die or multiple dice. ' +
                                  'It currently can handle rolls of the form xdy(k/d)z(!)(+/-)a(>/<)b, '
                                  'where x, y, z, and b are nonnegative integers, ' +
                                  'and where a is an integer. Regular dice, drop-keep syntax, ' +
                                  'exploding dice, challenge dice, and combinations of these are all supported. ' +
                                  'Only the the first "d" is required to perform a roll. ' +
                                  'The default x value is 1. The default y value is 6. The others default to 0. ' +
                                  'Quoted, a description of what the roll was for may be included afterward. ' +
                                  'The result is posted either in a set gamble channel or where the die was rolled.')
    async def chance(self, ctx, roll: str, description: str = 'To Contend with Lady Luck'):
        gamble_channel_id: int = Guild.get_gamble_channel_by(ctx.guild.id)
        current_channel = self.bot.get_channel(gamble_channel_id) if self.bot.get_channel(gamble_channel_id) \
            else ctx.message.channel
        flat_tokens, verbose_dice, roll_result = await self.handle_roll(ctx, roll)
        await self.send_roll(ctx, roll, flat_tokens, verbose_dice, roll_result, current_channel, description)

    @commands.command(description='This command gets Smorg to roll one die or multiple dice and ' +
                                  'to send the result to one or more recipients. ' +
                                  'These recipients are the second item to be typed in the command, ' +
                                  'presented in quotes as usernames or server nicknames and delimited by semicolons. ' +
                                  'The user is automatically listed as a recipient. ' +
                                  'See the documentation for "chance" for a description of the remaining syntax.')
    async def hazard(self, ctx, roll: str, recipients: str = None, description: str = 'To Contend with Lady Luck'):
        starting_chosen_recipients: list = [ctx.message.author]
        chosen_recipients: list = await self.get_recipients(ctx, recipients, starting_chosen_recipients) if recipients \
            else starting_chosen_recipients
        while chosen_recipients.count(ctx.message.author) > 1:
            chosen_recipients.remove(ctx.message.author)
        await self.inform_recipients(ctx, roll, chosen_recipients, description)

    @commands.command(description='This command gets Smorg to roll one die or multiple dice and ' +
                                  'to send the result to one or more recipients that do not include the user. ' +
                                  'These recipients are the second item to be typed in the command, ' +
                                  'presented in quotes as usernames or server nicknames and delimited by semicolons. ' +
                                  'See the documentation for "chance" for a description of the remaining syntax.')
    async def imperil(self, ctx, roll: str, recipients: str = None, description: str = 'To Contend with Lady Luck'):
        chosen_recipients: list = await self.get_recipients(ctx, recipients) if recipients \
            else await ctx.send("Error: no recipients were given for this roll.")
        if ctx.message.author in chosen_recipients:
            await ctx.send("Error: the sender is not allowed to be a recipient for this roll.")
        else:
            await self.inform_recipients(ctx, roll, chosen_recipients, description)

    async def get_recipients(self, ctx, recipients: str, chosen_recipients: list = None) -> list:
        if chosen_recipients is None:
            chosen_recipients = []

        ReducedMember = namedtuple('ReducedMember', 'nickname username id')
        guild_members: list = list(map(lambda member: ReducedMember(member.nick, member.name, member.id),
                                       ctx.guild.members))
        for recipient in recipients.split(';'):
            recipient = recipient.strip()
            found_recipients: list = []
            for reduced_member in guild_members:
                if recipient in [reduced_member.nickname, reduced_member.username]:
                    found_recipients.append(reduced_member)
            else:
                if len(found_recipients) == 0:
                    await ctx.send(f"Error: no individual matches the recipient name or nickname given for {recipient}."
                                   f" Please try again.")
                else:
                    chosen_recipient_index: int = await Disambiguator.disambiguate(self.bot, ctx, found_recipients)
                    chosen_recipient = self.bot.get_user(found_recipients[chosen_recipient_index].id)
                    chosen_recipients.append(chosen_recipient)
        return chosen_recipients

    async def inform_recipients(self, ctx, roll: str, chosen_recipients: list, description: str):
        flat_tokens, verbose_dice, roll_result = await self.handle_roll(ctx, roll)
        for chosen_recipient in chosen_recipients:
            if not chosen_recipient.dm_channel:
                await self.bot.get_user(chosen_recipient.id).create_dm()
            recipient_dm_channel = chosen_recipient.dm_channel
            await self.send_roll(ctx, roll, flat_tokens, verbose_dice, roll_result, recipient_dm_channel, description)

    async def handle_roll(self, ctx, roll: str):
        raw_roll: str = roll.replace(' ', '')
        parsed_roll: list = await self.parse_roll(raw_roll)
        verbose_dice: list = []
        for match_index, match in enumerate(parsed_roll):
            # TODO: add enum for readability
            if match[0]:
                parsed_dice = await self.parse_dice(match[0])
                processed_dice: dict = await self.process_dice(parsed_dice)
                dice_result, unsorted_results, sorted_results = await self.evaluate_roll(processed_dice)
                verbose_die: tuple = (match[0], unsorted_results, sorted_results, dice_result)
                verbose_dice.append(verbose_die)
                parsed_roll[match_index] = (str(dice_result),)
        flat_matches: list = [item for match in parsed_roll for item in match if item]
        roll_result = await self.yard_shunter.shunt_yard(ctx, flat_matches)
        return flat_matches, verbose_dice, roll_result

    @staticmethod
    async def send_roll(ctx, roll, flat_tokens, verbose_dice, roll_result, destination_channel, description):
        description: str = description.strip()
        # TODO: re-implement message length handling
        # message_length = len(ctx.message.author.mention) + len(roll) + len(description) + \
        #     MessageConstants.DEFAULT_MSG_CHARACTERS

        introductory_message: str = f"{ctx.message.author.mention}\n" \
                                    f"Roll: {roll}\n" \
                                    f"Reason: {description}"
        await destination_channel.send(introductory_message)

        if verbose_dice:
            roll_result_message = f"The results of the individual roll(s) inside the overall roll are as follows:"
            await destination_channel.send(roll_result_message)
            for (raw_roll, unsorted_result, sorted_result, dice_result) in verbose_dice:
                verbose_roll_message = f"\nThe roll {raw_roll} resulted in: \n**Raw Dice Result:** {unsorted_result} \n" \
                                       f"**Final Dice Result:** {sorted_result} \n**Sum:** {dice_result}"
                await destination_channel.send(verbose_roll_message)

        evaluated_roll: str = ""
        for token in flat_tokens:
            evaluated_roll += str(token)
        concluding_message = f"The evaluated roll was: {evaluated_roll}\n" \
                             f"The final result of this roll is: {roll_result}"
        await destination_channel.send(concluding_message)

    @staticmethod
    async def parse_roll(raw_roll):
        roll_pattern = re.compile(r'(?:(?P<roll>[\d]+[dD][\d]+(?:[dDkK][\d]+)?(?:!)?(?:[><][+-]?[\d]+)?)|'
                                  r'(?P<regular_operator>[+\-*/^])|'
                                  r'(?P<grouping_operator>[()])|'
                                  r'(?P<function>abs|floor|ceiling|sqrt)|'
                                  r'(?P<constant>[+-]?[\d]+))')
        return re.findall(roll_pattern, raw_roll)

    @staticmethod
    async def parse_dice(raw_dice):
        dice_pattern = re.compile(r'(?P<number_of_dice>[\d]+)[dD]'
                                  r'(?P<die_size>[\d]+)'
                                  r'(?P<drop_keep_sign>(?P<drop_sign>[dD])|(?P<keep_sign>[kK]))?'
                                  r'(?(drop_keep_sign)(?P<drop_keep_value>[\d]+))?'
                                  r'(?P<explosion_sign>!)?'
                                  r'(?P<challenge_sign>[><])?'
                                  r'(?(challenge_sign)(?P<challenge_value>[+-]?[\d]+))')
        return re.match(dice_pattern, raw_dice)

    @staticmethod
    async def process_dice(matched_dice):
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

    async def evaluate_roll(self, processed_roll):
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
    async def roll_dice(number_of_dice, die_size, explosion_sign):
        roll_list: list = []
        roll_index: int = 0
        while roll_index < number_of_dice:
            single_roll = randint(1, die_size)
            roll_list.append(single_roll)
            if not (explosion_sign and single_roll == die_size):
                roll_index += 1
        return roll_list

    @staticmethod
    async def select_dice(roll_list, drop_sign, keep_sign, drop_keep_value):
        if drop_sign:
            del roll_list[(len(roll_list) - drop_keep_value):]
        elif keep_sign:
            del roll_list[drop_keep_value:]
        return roll_list

    @staticmethod
    async def analyze_roll(roll_list, challenge_sign, challenge_value):
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
