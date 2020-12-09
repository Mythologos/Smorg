
import tempfile

from discord import File, TextChannel
from discord.ext import commands
from tempfile import NamedTemporaryFile

from .Helpers.Enumerators.universalist import HelpDescription, StaticText


class Logger(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description=HelpDescription.LOG)
    async def log_channel(self, ctx: commands.Context, channel: TextChannel) -> None:
        temporary_file: NamedTemporaryFile = NamedTemporaryFile(suffix='.txt', prefix=f'log_{channel.name}')

        async for message in channel.history(oldest_first=True):
            # Process:
            # (1) Check the sender of the current message.
            # (1a) If they're the same as the previous sender, continue.
            # (1b) If they're not the same as the previous sender, denote them as the previous sender.
            # (2) Format the message appropriately, removing any extraneous information or characters if necessary.
            # Use the given information (options, character-user links) to do this accordingly.
            # (3) Put the message in the file. Proceed.
            ...

        # Upload the file to Discord.
        await ctx.send(StaticText.LOG_DEFAULT_TEXT, file=temporary_file)

        # Finally, destroy the file locally by closing it.
        temporary_file.close()
        # to consider: text options?
        # to consider: how to relate users and characters; do I want to have a "general log" and an "RP log" option
