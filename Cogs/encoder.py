# TODO: overall documentation
# TODO: perhaps transition dictionaries into default_dicts?
# TODO: more rigorous handling of parentheses in morse_to_alphabet
# TODO: add easier way to write morse-like code with period and dash characters
# The morse code is based on: http://ascii-table.com/morse-code.php

from discord.ext import commands

from Cogs.Helpers.exceptioner import MissingSubcommand
from Cogs.Helpers.Enumerators.universalist import DiscordConstant, HelpDescription, MessageConstant


class Encoder(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.morse_to_alphabet = {
            '• −': 'a',
            '− • • •': 'b',
            '− • − •': 'c',
            '− • •': 'd',
            '•': 'e',
            '• • − •': 'f',
            '− − •': 'g',
            '• • • •': 'h',
            '• •': 'i',
            '• − − −': 'j',
            '− • −': 'k',
            '• − • •': 'l',
            '− −': 'm',
            '− •': 'n',
            '− − −': 'o',
            '• − − •': 'p',
            '− − • −': 'q',
            '• − •': 'r',
            '• • •': 's',
            '−': 't',
            '• • −': 'u',
            '• • • −': 'v',
            '• − −': 'w',
            '− • • −': 'x',
            '− • − −': 'y',
            '− − • •': 'z',
            '− − − − −': '0',
            '• − − − −': '1',
            '• • − − −': '2',
            '• • • − −': '3',
            '• • • • −': '4',
            '• • • • •': '5',
            '− • • • •': '6',
            '− − • • •': '7',
            '− − − • •': '8',
            '− − − − •': '9',
            '• − • − • −': '.',
            '− − • • − −': ',',
            '− − − • • •': ':',
            '• • − − • •': '?',
            '• − − − − •': '\'',
            '− • • • • −': '-',
            '− • • − •': '/',
            '− • − − • −': '|',
            '• − • • − •': '\"',
            '• − − • − •': '@',
            '− • • • −': '=',
            '• • • • • • • •': '[ERROR]',
            '  /  ': ' '
        }
        self.alphabet_to_morse = {
            'a': '• −',
            'b': '− • • •',
            'c': '− • − •',
            'd': '− • •',
            'e': '•',
            'f': '• • − •',
            'g': '− − •',
            'h': '• • • •',
            'i': '• •',
            'j': '• − − −',
            'k': '− • −',
            'l': '• − • •',
            'm': '− −',
            'n': '− •',
            'o': '− − −',
            'p': '• − − •',
            'q': '− − • −',
            'r': '• − •',
            's': '• • •',
            't': '−',
            'u': '• • −',
            'v': '• • • −',
            'w': '• − −',
            'x': '− • • −',
            'y': '− • − −',
            'z': '− − • •',
            '0': '− − − − −',
            '1': '• − − − −',
            '2': '• • − − −',
            '3': '• • • − −',
            '4': '• • • • −',
            '5': '• • • • •',
            '6': '− • • • •',
            '7': '− − • • •',
            '8': '− − − • •',
            '9': '− − − − •',
            '.': '• − • − • −',
            ',': '− − • • − −',
            ':': '− − − • • •',
            '?': '• • − − • •',
            '\'': '• − − − − •',
            '-': '− • • • • −',
            '/': '− • • − •',
            '(': '− • − − • −',
            ')': '− • − − • −',
            '[': '− • − − • −',
            ']': '− • − − • −',
            '{': '− • − − • −',
            '}': '− • − − • −',
            '\"': '• − • • − •',
            '@': '• − − • − •',
            '=': '− • • • −',
            '[ERROR]': '• • • • • • • •',
            ' ': '  /  '
        }

    @commands.group(description=HelpDescription.TRANSLATE)
    async def translate(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand

    @translate.group(name='alphabet')
    async def from_alphabet(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand(2)

    @from_alphabet.command(name='morse')
    async def to_morse(self, ctx: commands.Context, quote: str) -> None:
        morse_quote: str = ''
        for index, character in enumerate(quote.lower()):
            try:
                morse_quote += self.alphabet_to_morse[character]
                if character != ' ' and ((index < (len(quote) - 1)) and quote[index + 1] != ' '):
                    morse_quote += '   '
            except KeyError:
                morse_quote += self.alphabet_to_morse['[ERROR]']
        await self.send_translation(ctx, morse_quote, "alphabetical", "morse", "/")

    @translate.group(name='morse')
    async def from_morse(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand(2)

    @from_morse.command(name='alphabet')
    async def to_alphabet(self, ctx: commands.Context, quote: str) -> None:
        alphabetical_quote: str = ''
        spaced_quote: list = quote.split('  /  ')
        for word in spaced_quote:
            characters = word.split('   ')
            for character in characters:
                alphabetical_quote += self.morse_to_alphabet[character]
            alphabetical_quote += ' '
        await self.send_translation(ctx, alphabetical_quote, "morse", "alphabetical")

    async def send_translation(self, ctx: commands.Context, translated_message: str, from_language: str,
                               to_language: str, split_separator: str = " ") -> None:
        message_introduction: str = f"The {to_language} translation of your {from_language} input is: \n"
        if await self.message_does_fit(DiscordConstant.MAX_MESSAGE_LENGTH, translated_message, message_introduction):
            await ctx.send(f"{message_introduction}{translated_message}")
        else:
            safe_maximum_message_length: int = DiscordConstant.MAX_MESSAGE_LENGTH - (
                    len(message_introduction) + MessageConstant.TRANSLATION_ADDITIONAL_CHARACTERS
            )
            compact_messages: list = await self.condense(
                translated_message, split_separator, safe_maximum_message_length
            )
            for index, message in enumerate(compact_messages, start=1):
                if index == 1:
                    await ctx.send(f"{message_introduction}{message} . . .")
                elif index != len(compact_messages):
                    await ctx.send(f". . . {message} . . .")
                else:
                    await ctx.send(f". . . {message}")

    @staticmethod
    async def message_does_fit(maximum_length: int, main_message: str, *additional_messages) -> bool:
        does_message_fit: bool = True
        if sum([len(message) for message in additional_messages], len(main_message)) > maximum_length:
            does_message_fit = False
        return does_message_fit

    async def condense(self, message: str, split_separator: str, maximum_length: int) -> list:
        if split_separator in message:
            compact_messages: list = await self.guided_condense(message, split_separator, maximum_length)
            for index, component_message in enumerate(compact_messages):
                if len(component_message) > maximum_length:
                    compact_segment_messages: list = await self.automated_condense(component_message, maximum_length)
                    compact_segment_messages.reverse()
                    del compact_messages[index]
                    for segment_message in compact_segment_messages:
                        compact_messages.insert(index, segment_message)
        else:
            compact_messages: list = await self.automated_condense(message, maximum_length)
        return compact_messages

    @staticmethod
    async def guided_condense(message: str, split_separator: str, maximum_length: int) -> list:
        compact_messages: list = []
        message_units: list = message.split(split_separator)
        compact_unit: str = ""
        for index, unit in enumerate(message_units, start=1):
            if index != len(message_units):
                unit += split_separator
            if (len(compact_unit) + len(unit)) > maximum_length:
                if compact_unit:
                    compact_messages.append(compact_unit)
                compact_unit = unit
            else:
                compact_unit += unit
        compact_messages.append(compact_unit)
        return compact_messages

    @staticmethod
    async def automated_condense(message: str, maximum_length: int) -> list:
        compact_messages: list = []
        total_length: int = len(message)
        while total_length > 0:
            compact_messages.append(message[0:maximum_length])
            print(compact_messages)
            message = message[maximum_length:]
            total_length -= maximum_length
        return compact_messages
