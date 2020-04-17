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


class InvalidDay(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class InvalidHour(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class InvalidMinute(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class InvalidMonth(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class InvalidTimeZone(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class InvalidYear(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class EmptyEmbed(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)


class MissingSubcommand(commands.UserInputError):
    def __init__(self, subcommand_depth: int = 1, message: str = None, *args):
        self.subcommand_depth: int = subcommand_depth
        super().__init__(message=message, *args)


class MissingReminder(commands.UserInputError):
    def __init__(self, message: str = None, *args):
        super().__init__(message=message, *args)
