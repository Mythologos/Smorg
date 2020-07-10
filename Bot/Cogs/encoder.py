"""
This module contains the encoder Cog. It revolves around the translate Command and, with this command,
it translates items of one character set into another character set.

The morse code in the encoder Cog is based on: http://ascii-table.com/morse-code.php
"""

from discord.ext import commands

from Bot.Cogs.Helpers.condenser import Condenser
from Bot.Cogs.Helpers.exceptioner import MissingSubcommand
from Bot.Cogs.Helpers.Enumerators.polyglot import AlphabetDictionary
from Bot.Cogs.Helpers.Enumerators.universalist import DiscordConstant, HelpDescription


class Encoder(commands.Cog, Condenser):
    """
    This class centers around the translate method, declaring AlphabetDictionary constants for translation purposes
    and using the Condenser class to translate a message of one character set into one of another character set
    and send it without defying Discord's message size limitations.
    """
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        # Dictionaries don't seem to unpack for natural use from their NamedConstant-subclassed objects.
        # Not completely sure why this is, but their values can be accessed from the protected attribute _value_.
        # I avoided direct access on principle, but I still don't like this idiom.
        self.alphabet_to_morse = AlphabetDictionary.ALPHABET_TO_MORSE.__getattribute__('_value_')
        self.morse_to_alphabet = AlphabetDictionary.MORSE_TO_ALPHABET.__getattribute__('_value_')

    @commands.group(description=HelpDescription.TRANSLATE)
    async def translate(self, ctx: commands.Context) -> None:
        """
        This method is the central Command for this Cog, translating one set of characters into another.
        It has two layers of subcommands, each of which consist of the same items.
        The first is the character set of the given text; the second is the character set of the output text.
        Valid subcommands include alphabet and morse.

        :param commands.Context ctx: the context from which the command was made.
        """
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand

    @translate.group(name='alphabet')
    async def from_alphabet(self, ctx: commands.Context) -> None:
        """
        This is a first subcommand of the translate Command. It indicates that alphabet is the starting character set
        for the translation.

        :param commands.Context ctx: the context from which the command was made.
        """
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand(2)

    @from_alphabet.command(name='morse')
    async def to_morse(self, ctx: commands.Context, quote: str) -> None:
        """
        This is a second subcommand of the translate Command. It indicates that morse is the target character set
        for translation.

        :param commands.Context ctx: the context from which the command was made.
        :param str quote: the text which is to be transferred from one character set to morse.
        """
        morse_quote: str = 'The morse translation of your alphabetical input is: \n'
        for index, character in enumerate(quote.lower()):
            try:
                morse_quote += self.alphabet_to_morse[character]
                if character != ' ' and ((index < (len(quote) - 1)) and quote[index + 1] != ' '):
                    morse_quote += '   '
            except KeyError:
                morse_quote += self.alphabet_to_morse['[ERROR]']
        await self.send_condensed_message(ctx.channel, morse_quote, DiscordConstant.MAX_MESSAGE_LENGTH, "/")

    @translate.group(name='morse')
    async def from_morse(self, ctx: commands.Context) -> None:
        """
        This is a first subcommand of the translate Command. It indicates that morse is the starting character set
        for the translation.

        :param commands.Context ctx: the context from which the command was made.
        """
        if ctx.invoked_subcommand is None:
            raise MissingSubcommand(2)

    @from_morse.command(name='alphabet')
    async def to_alphabet(self, ctx: commands.Context, quote: str) -> None:
        """
        This is a second subcommand of the translate Command. It indicates that alphabet is the target character set
        for translation.

        :param commands.Context ctx: the context from which the command was made.
        :param str quote: the text which is to be transferred from one character set to the alphabet.
        """
        alphabetical_quote: str = 'The alphabetical translation of your morse input is: \n'
        spaced_quote: list = quote.split('  /  ')
        for word in spaced_quote:
            characters = word.split('   ')
            for character in characters:
                alphabetical_quote += self.morse_to_alphabet[character]
            alphabetical_quote += ' '
        await self.send_condensed_message(ctx.channel, alphabetical_quote, DiscordConstant.MAX_MESSAGE_LENGTH)
