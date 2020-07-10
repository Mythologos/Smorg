"""
This module contains the Condenser mix-in, which helps various Command objects produce messages for Discord
that do not exceed message limits and wrap nicely into multiple messages.
"""

from discord import TextChannel

from Bot.Cogs.Helpers.Enumerators.universalist import MessageConstant


class Condenser:
    """
    This class contains methods to help assure that a message can be sent within Discord's parameters.
    Its goals are to split rather than to truncate. It centers around the send_condensed_message() function,
    which calls other methods in the class as needed in order to prepare a given message for sending.
    It either splits a message based on the maximum message length or uses a separator to cut the message
    at certain natural locations.
    """
    async def send_condensed_message(self, destination_channel: TextChannel, message: str, maximum_length: int,
                                     split_separator: str = " ") -> None:
        """
        This method sends a message to a channel and splits it up as needed in order to avoid exceeding
        Discord's message limits.

        :param TextChannel destination_channel: the place to which the given message is to be sent.
        :param str message: the text that is to be split up and sent to Discord.
        :param int maximum_length: the total number of characters that a message should not exceed.
        :param str split_separator: a common separator inside of a message that could be used
        to split it up more naturally.
        """
        if len(message) <= maximum_length:
            await destination_channel.send(message)
        else:
            safe_maximum_message_length: int = maximum_length - MessageConstant.CONDENSE_CHARACTERS
            compact_messages: list = await self.condense(message, split_separator, safe_maximum_message_length)
            for counter, message_segment in enumerate(compact_messages, start=1):
                if counter == 1:
                    await destination_channel.send(f"{message_segment} . . .")
                elif counter != len(compact_messages):
                    await destination_channel.send(f". . . {message_segment} . . .")
                else:
                    await destination_channel.send(f". . . {message_segment}")

    async def condense(self, message: str, split_separator: str, maximum_length: int) -> list:
        """
        This method splits a message into smaller pieces so that Discord can send the full message.
        It does so through two separate algorithms--guided_condense() and automated_condense().
        For the former to work, the given separator must be deemed efficient.
        Otherwise, the latter can always be employed to split a message at even segments.

        :param str message: the text to be condensed.
        :param str split_separator: the recommended textual separator for guided_condense().
        :param int maximum_length: the length which a given message cannot exceed in order for it to be sent.
        :return list: a collection of the messages which Discord can send; all text and order from message
        should be preserved.
        """
        if await self.is_efficient_separator(message, split_separator, maximum_length):
            compact_messages: list = await self.guided_condense(message, split_separator, maximum_length)
        else:
            compact_messages: list = await self.automated_condense(message, maximum_length)
        return compact_messages

    @staticmethod
    async def is_efficient_separator(message: str, split_separator: str, maximum_length: int) -> bool:
        """
        This method determines whether a separator is efficient enough to be used for guided_condense().
        Efficiency is based on the idea that the distance between every two separators in a message is
        less than the maximum_length.

        :param str message: the text to be condensed.
        :param str split_separator: the recommended textual separator for guided_condense().
        :param int maximum_length: the length which a given message cannot exceed in order for it to be sent.
        :return bool: True if there is a separator within every maximum_length distance in the message.
        """
        first_index: int = 0
        separator_is_efficient: bool = True
        while first_index != MessageConstant.NOT_FOUND_INDEX:
            second_index = message.find(split_separator, first_index + 1)
            if second_index != MessageConstant.NOT_FOUND_INDEX and (second_index - first_index) > maximum_length:
                separator_is_efficient = False
                break
            first_index = second_index
        return separator_is_efficient

    @staticmethod
    async def guided_condense(message: str, split_separator: str, maximum_length: int) -> list:
        """
        This method divides up a message based on a separating character. To do so, it splits the message
        into segments with split() and this separator; then, it puts the message back together based on
        these split units until the message reaches a size at which adding more would cause it to go over
        maximum_length.

        :param str message: the text to be condensed.
        :param str split_separator: the recommended textual separator for guided_condense().
        :param int maximum_length: the length which a given message cannot exceed in order for it to be sent.
        :return list: a collection of messages split by split_separator and less than maximum_length in size.
        """
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
        """
        This method cuts a message into chunks of maximum_length size. It returns these chunks in a list.

        :param str message: the text to be condensed.
        :param int maximum_length: the length which a given message cannot exceed in order for it to be sent.
        :return list: a collection of messages less than maximum_length in size.
        """
        compact_messages: list = []
        total_length: int = len(message)
        while total_length > 0:
            compact_messages.append(message[0:maximum_length])
            message = message[maximum_length:]
            total_length -= maximum_length
        return compact_messages
