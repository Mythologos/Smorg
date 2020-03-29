# TODO: documentation...

from discord.ext import commands


class DuplicateOperator(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class ImproperFunction(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class MissingParenthesis(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class InvalidRecipient(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)
