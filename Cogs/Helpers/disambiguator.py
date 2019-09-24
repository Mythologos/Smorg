import discord


# describe as Cog mixin
class Disambiguator:
    @staticmethod
    async def disambiguate(bot, ctx, options):
        option_index: int = 0   # note this as default value for option_index
        if len(options) > 1:
            selection_message: str = 'Please select an item from the following options via its number: /n'
            for index, item in enumerate(options):
                selection_message = selection_message + str(index + 1) + ": " + str(item) + "/n"
            await ctx.send(selection_message)
            try:
                option_index: str = await bot.wait_for('message',
                                                       timeout=120.0,
                                                       check=lambda msg: (msg.author == ctx.author) and
                                                                         (0 < int(msg) <= len(options)))
                option_index: int = int(option_index) - 1
            except TimeoutError:
                disambiguation_timeout_embed = discord.Embed(title='Error: Disambiguation Timeout',
                                                             description='You didn\'t supply a valid index quickly enough.',
                                                             color=0xB80000)
                await ctx.send(embed=disambiguation_timeout_embed)
        return option_index
