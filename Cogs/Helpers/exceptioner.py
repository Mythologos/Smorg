"""
This module contains various custom errors for Smorg and the Exceptioner mix-in.
The latter item helps to produce error Embeds to be posted on Discord.
"""

from discord import Embed
from discord.ext.commands import UserInputError
from typing import Union

from Cogs.Helpers.Enumerators.universalist import ColorConstant


class Exceptioner:
    """
    This class is a mix-in that helps various Cogs to compose error embeds.
    """
    @staticmethod
    async def initialize_error_embed(command_name: str, error_name: str, error_description: str) -> Embed:
        """
        This method composes an embed to display an error based on certain identifying attributes.

        :param str command_name: the name of the command for which an error is being raised.
        :param str error_name: the name of the error that is being raised.
        :param str error_description: the description of the error that is being raised.
        :return Embed: a completed Discord Embed containing the above elements.
        """
        return Embed(
            title=f'Error ({command_name}): {error_name}',
            description=error_description,
            color=ColorConstant.ERROR_RED
        )

    @staticmethod
    async def compose_error_name(class_name: str) -> str:
        """
        This method helps to make an error's name more reasonable for presentation.
        For error names that are taken from the __name__ field, this function adds spaces
        between individual characters in accordance with exceptions' camel case.

        :param str class_name: the name of an exception.
        :return str: the name of an exception with its component words appropriately spaced.
        """
        spaced_class_name: str = ""
        for index, character in enumerate(class_name):
            if character.isupper():
                spaced_class_name += " "
            spaced_class_name += character
        return spaced_class_name


class DuplicateOperator(UserInputError):
    """
    This exception indicates that multiple operators appear consecutively in an illegal manner
    in a mathematical expression.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class ImproperFunction(UserInputError):
    """
    This exception indicates that a mathematical function does not have parentheses surrounding its argument.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class MissingParenthesis(UserInputError):
    """
    This exception indicates that a mathematical expression is missing a parenthesis where one is required
    (e.g. to balance another).
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidRecipient(UserInputError):
    """
    The exception indicates that a given recipient was not recognized.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidDay(UserInputError):
    """
    The exception indicates that a given day is not valid in processing datetime objects.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidHour(UserInputError):
    """
    The exception indicates that a given hour is not valid in processing datetime objects.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidMinute(UserInputError):
    """
    The exception indicates that a given minute is not valid in processing datetime objects.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidMonth(UserInputError):
    """
    The exception indicates that a given month is not valid in processing datetime objects.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidTimeZone(UserInputError):
    """
    This exception indicates that a given time zone is not valid in processing datetime objects.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidYear(UserInputError):
    """
    This exception indicates that a given year is not valid in processing datetime objects.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class EmptyEmbed(UserInputError):
    """
    This exception indicates that an embed contains no content and will not be outputted.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class MissingSubcommand(UserInputError):
    """
    This exception indicates that a Command that required a subcommand was not given one.
    Subcommand depth indicates how many subcommand levels deep that subcommand was.
    For example, the translate Command has two levels of subcommands--the language that Smorg translates from
    and the language that Smorg translates to.
    """
    def __init__(self, subcommand_depth: int = 1, message: Union[str, None] = None, *args):
        self.subcommand_depth: int = subcommand_depth
        super().__init__(message=message, *args)


class MissingReminder(UserInputError):
    """
    This exception indicates that a reminder with given attributes was not found.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidRoll(UserInputError):
    """
    This exception indicates that a user's given roll is invalid, as not all of the inputted characters were accepted.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidSequence(UserInputError):
    """
    This exception indicates that there is an invalid sequence of mathematical characters within a calculation.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidFunction(UserInputError):
    """
    This exception indicates that there is an invalid function in a calculation.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidOperator(UserInputError):
    """
    This exception indicates that there is an invalid operator in a calculation.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidComparison(UserInputError):
    """
    This exception indicates that there is an invalid comparison operator in use.
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)
