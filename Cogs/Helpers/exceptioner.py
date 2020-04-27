"""
...
"""

from discord import Embed
from discord.ext.commands import UserInputError
from typing import Union

from Cogs.Helpers.Enumerators.universalist import ColorConstant


class Exceptioner:
    """
    ...
    """
    @staticmethod
    async def initialize_error_embed(command_name: str, error_name: str, error_description: str) -> Embed:
        """
        ...

        :param str command_name:
        :param str error_name:
        :param str error_description:
        :return Embed:
        """
        return Embed(
            title=f'Error ({command_name}): {error_name}',
            description=error_description,
            color=ColorConstant.ERROR_RED
        )

    @staticmethod
    async def compose_error_name(class_name: str) -> str:
        """
        ...

        :param str class_name:
        :return str:
        """
        spaced_class_name: str = ""
        for index, character in enumerate(class_name):
            if character.isupper():
                spaced_class_name += " "
            spaced_class_name += character
        return spaced_class_name


class DuplicateOperator(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class ImproperFunction(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class MissingParenthesis(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidRecipient(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidDay(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidHour(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidMinute(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidMonth(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidTimeZone(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidYear(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class EmptyEmbed(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class MissingSubcommand(UserInputError):
    """
    ...
    """
    def __init__(self, subcommand_depth: int = 1, message: Union[str, None] = None, *args):
        self.subcommand_depth: int = subcommand_depth
        super().__init__(message=message, *args)


class MissingReminder(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidRoll(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)


class InvalidSequence(UserInputError):
    """
    ...
    """
    def __init__(self, message: Union[str, None] = None, *args):
        super().__init__(message=message, *args)
