"""
...
"""

from discord import TextChannel

from Cogs.Helpers.Enumerators.universalist import MessageConstant


class Condenser:
    """
    ...
    """
    async def send_condensed_message(self, destination_channel: TextChannel, message: str, maximum_length: int,
                                     split_separator: str = " ") -> None:
        """
        ...
        :param destination_channel:
        :param message:
        :param maximum_length:
        :param split_separator:
        :return:
        """
        if len(message) <= maximum_length:
            await destination_channel.send(message)
        else:
            safe_maximum_message_length: int = maximum_length - MessageConstant.CONDENSE_CHARACTERS
            compact_messages: list = await self.condense(message, split_separator, safe_maximum_message_length)
            for index, message_segment in enumerate(compact_messages, start=1):
                if index == 1:
                    await destination_channel.send(f"{message_segment} . . .")
                elif index != len(compact_messages):
                    await destination_channel.send(f". . . {message_segment} . . .")
                else:
                    await destination_channel.send(f". . . {message_segment}")

    async def condense(self, message: str, split_separator: str, maximum_length: int) -> list:
        """
        ...
        :param message:
        :param split_separator:
        :param maximum_length:
        :return:
        """
        if await self.is_efficient_separator(message, split_separator, maximum_length):
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
    async def is_efficient_separator(message: str, split_separator: str, maximum_length: int) -> bool:
        """
        ...
        :param message:
        :param split_separator:
        :param maximum_length:
        :return:
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
        ...
        :param message:
        :param split_separator:
        :param maximum_length:
        :return:
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
        ...
        :param message:
        :param maximum_length:
        :return:
        """
        compact_messages: list = []
        total_length: int = len(message)
        while total_length > 0:
            compact_messages.append(message[0:maximum_length])
            message = message[maximum_length:]
            total_length -= maximum_length
        return compact_messages
