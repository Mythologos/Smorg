# TODO: overall documentation
# TODO: deck of cards.
# TODO: warnings / safeguards against generating a message longer than 2000 characters.
# TODO: exceptions for incorrect roll syntax. (e.g.: challenge rolls that end up using characters.)
# TODO: divide up some of these functions; some are getting decently long.
# TODO: allow and pre-remove spaces in roll syntax

from discord.ext import commands
from smorgasDB import Guild
from Cogs.Helpers.disambiguator import Disambiguator
from Cogs.Helpers.Enumerators.croupier import RollComponent, RollParseResult, RollResult, \
    ComparisonIndicator, DropKeepIndicator
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
        roll_results: tuple = await self.handle_roll(ctx, roll)
        await self.send_roll(ctx, roll, roll_results[0], roll_results[1], current_channel, description)

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
                    await ctx.send("Error: no individual matches the recipient name or nickname given for " +
                                   recipient + "." + "Please try again.")
                else:
                    chosen_recipient_index: int = await Disambiguator.disambiguate(self.bot, ctx, found_recipients)
                    chosen_recipient = self.bot.get_user(found_recipients[chosen_recipient_index].id)
                    chosen_recipients.append(chosen_recipient)
        return chosen_recipients

    async def inform_recipients(self, ctx, roll: str, chosen_recipients: list, description: str):
        roll_results: tuple = await self.handle_roll(ctx, roll)
        for chosen_recipient in chosen_recipients:
            if not chosen_recipient.dm_channel:
                await self.bot.get_user(chosen_recipient.id).create_dm()
            recipient_dm_channel = chosen_recipient.dm_channel
            await self.send_roll(ctx, roll, roll_results[0], roll_results[1],
                                 recipient_dm_channel, description)

    async def handle_roll(self, ctx, roll: str):
        roll: str = roll.strip()
        roll_parse_result: list = await self.parse_roll(ctx, roll)
        roll_result: tuple = await self.evaluate_roll(roll_parse_result)
        return roll_parse_result, roll_result

    async def send_roll(self, ctx, roll, roll_parse_result, roll_result, destination_channel, description):
        description: str = description.strip()
        raw_result_message: str = await self.format_roll_result(roll_result[RollResult.UNSORTED_RESULTS.value])
        end_result_message: str = await self.format_roll_result(roll_result[RollResult.INDIVIDUAL_RESULTS.value])
        modifier_message: str = " + " + str(roll_parse_result[RollParseResult.OVERALL_MODIFIER.value]) \
            if roll_parse_result[RollParseResult.OVERALL_MODIFIER.value] != 0 else ""
        gamble_message = ctx.message.author.mention + "\n" + \
            "Roll: " + roll + "\n" + \
            "Reason: " + description + "\n" + \
            "Raw Result: " + "(" + raw_result_message + ")" + modifier_message + "\n" + \
            "End Result: " + "(" + end_result_message + ")" + modifier_message + \
            " = " + str(roll_result[RollResult.FINAL_RESULT.value])
        if roll_parse_result[RollParseResult.CHALLENGE_INDICATOR.value]:
            gamble_message += " Successes"
        await destination_channel.send(gamble_message)

    async def parse_roll(self, ctx, roll: str) -> list:
        roll_regex = re.compile('(\d*)[dD](\d*)([dkDK][\d]+)?([!])?([+-/\*\^\(\)' +
                                '(?:abs)(?:floor)(?:ceiling)(?:sqrt)\d]+)?([><][-]?\d+)?')
        regex_result = roll_regex.match(roll)
        roll_components: list = []
        roll_list: list = []
        try:
            assert regex_result
            for i in range(1, 1 + len(regex_result.groups())):
                roll_components.append(regex_result.group(i))
        except AssertionError:
            await ctx.send("Error: the syntax for the roll was invalid. Please try again.")
        else:
            number_rolls = await self.check_basic_roll_component(1, roll_components[RollComponent.NUMBER_OF_DICE.value])
            roll_list.append(number_rolls)
            die_size = await self.check_basic_roll_component(6, roll_components[RollComponent.DIE_SIZE.value])
            roll_list.append(die_size)

            die_count_modifier = await self.check_basic_roll_component(number_rolls, roll_components[
                RollComponent.DROP_KEEP_VALUE.value], 1)
            die_count_modifier, drop_keep_indicator = await self.parse_die_count_modifier(ctx, roll_components,
                                                                                          die_count_modifier,
                                                                                          number_rolls)
            roll_list.append(die_count_modifier)
            roll_list.append(drop_keep_indicator)

            die_explosion: bool = (roll_components[RollComponent.EXPLOSION_VALUE.value] == '!')
            roll_list.append(die_explosion)

            die_roll_modifier = await self.yard_shunter.shunt_yard(ctx, roll_components[
                RollComponent.OVERALL_MODIFIER.value]) if roll_components[
                RollComponent.OVERALL_MODIFIER.value] else 0
            roll_list.append(die_roll_modifier)

            die_challenge_value = int(roll_components[RollComponent.CHALLENGE_VALUE.value][1:]) \
                if roll_components[RollComponent.CHALLENGE_VALUE.value] and \
                await self.validate_integer(roll_components[RollComponent.CHALLENGE_VALUE.value][1:]) \
                else 0
            roll_list.append(die_challenge_value)

            if roll_components[RollComponent.CHALLENGE_VALUE.value]:
                if roll_components[RollComponent.CHALLENGE_VALUE.value][0:1] == '>':
                    roll_list.append(ComparisonIndicator.GREATER_THAN.value)
                else:
                    roll_list.append(ComparisonIndicator.LESS_THAN.value)
            else:
                roll_list.append(0)
        finally:
            return roll_list

    @staticmethod
    async def parse_die_count_modifier(ctx, roll_components, die_count_modifier, number_rolls):
        drop_keep_indicator = DropKeepIndicator.NONE.value
        try:
            assert (roll_components[RollComponent.DROP_KEEP_VALUE.value] and die_count_modifier <= number_rolls) or \
                    not roll_components[RollComponent.DROP_KEEP_VALUE.value]
        except AssertionError:
            await ctx.send("Error: The quantity given for the drop-keep roll number was not valid. Please try again.")
        else:
            if roll_components[RollComponent.DROP_KEEP_VALUE.value] and die_count_modifier <= number_rolls:
                if roll_components[RollComponent.DROP_KEEP_VALUE.value][0:1] in ['d', 'D']:
                    die_count_modifier = number_rolls - die_count_modifier
                    drop_keep_indicator = DropKeepIndicator.DROP.value
                else:
                    drop_keep_indicator = DropKeepIndicator.KEEP.value
        return die_count_modifier, drop_keep_indicator

    @staticmethod
    async def evaluate_roll(roll_parse_result: list) -> tuple:
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
        if roll_parse_result[RollParseResult.DROP_KEEP_INDICATOR.value] == DropKeepIndicator.DROP.value:
            del individual_results[(roll_parse_result[RollParseResult.DROP_KEEP_VALUE.value] + explosion_count):]
        else:
            del individual_results[roll_parse_result[RollParseResult.DROP_KEEP_VALUE.value]:]

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
        return roll_result, unsorted_results, individual_results

    @staticmethod
    async def format_roll_result(roll_sequence: list):
        result_message: str = ''
        for result in roll_sequence:
            if result_message:
                result_message = result_message + ' + ' + str(result)
            else:
                result_message = str(result)
        return result_message

    @staticmethod
    async def check_basic_roll_component(default_quantity: int, item: str, character_range_start: int = 0,
                                         character_range_end: int = None):
        roll_component_value: int = default_quantity
        if item and item[character_range_start:character_range_end].isdigit():
            roll_component_value = int(item[character_range_start:character_range_end])
        return roll_component_value

    @staticmethod
    async def validate_integer(value: str):
        validation_boolean: bool = False
        if value.isdecimal() or (value[0:1] == '-' and value[1:].isdecimal()):
            validation_boolean = True
        return validation_boolean
