# TODO: documentation...
# describe as Cog mixin

import discord


class Disambiguator:
    @staticmethod
    async def disambiguate(bot, ctx, options):
        option_index: int = 0   # note this as default value for option_index
        if len(options) > 1:
            selection_message: str = 'Please select an item from the following options via its number:\n'
            for index, item in enumerate(options, 1):
                selection_message += f"{index}: {item}\n"
            await ctx.send(selection_message)
            option_index: str = await bot.wait_for(
                'message',
                timeout=120.0,
                check=lambda msg: (msg.author == ctx.author) and (0 < int(msg) <= len(options)))
            option_index: int = int(option_index) - 1
        return option_index
