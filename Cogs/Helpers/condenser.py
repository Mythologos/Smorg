# TODO: documentation...


class Condenser:
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
            message = message[maximum_length:]
            total_length -= maximum_length
        return compact_messages
