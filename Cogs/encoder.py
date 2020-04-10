# TODO: overall documentation
# TODO: more rigorous handling of parentheses in morse_to_alphabet
# TODO: add easier way to write morse-like code with period and dash characters
# TODO: add better error-handling
# The morse code is based on: http://ascii-table.com/morse-code.php

from discord.ext import commands

from Cogs.Helpers.Enumerators.universalist import HelpDescription


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
            # TODO: change to raise error, add to error handling
            await ctx.send("An argument for the starting language was not found. Please try again.")

    @translate.group(name='alphabet')
    async def from_alphabet(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            # TODO: change to raise error, add to error handling
            await ctx.send("An argument for the target language was not found. Please try again.")

    @from_alphabet.command(name='morse')
    async def to_morse(self, ctx: commands.Context, quote: str) -> None:
        morse_quote: str = ''
        for index, character in enumerate(quote.lower()):
            morse_quote += self.alphabet_to_morse[character]
            if character != ' ' and ((index < (len(quote) - 1)) and quote[index + 1] != ' '):
                morse_quote += '   '
        await ctx.send(f"The morse translation of your alphabetical input is: \n{morse_quote}")

    @translate.group(name='morse')
    async def from_morse(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("An argument for the target language was not found. Please try again.")

    @from_morse.command(name='alphabet')
    async def to_alphabet(self, ctx: commands.Context, quote: str) -> None:
        alphabetical_quote: str = ''
        spaced_quote: list = quote.split('  /  ')
        for word in spaced_quote:
            characters = word.split('   ')
            for character in characters:
                alphabetical_quote += self.morse_to_alphabet[character]
            alphabetical_quote += ' '
        await ctx.send(f"The alphabetical translation of your morse input is: \n{alphabetical_quote}")
