
import os
import re

from datetime import datetime
from typing import Union

from discord import File, Member, TextChannel, User
from discord.ext import commands

from .Helpers.Enumerators.universalist import HelpDescription, StaticText
from .Helpers.Enumerators.polyglot import FormatDictionary


class Logger(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        #  See the encoder class for a discussion of this idiom.
        self.markdown_to_rtf = FormatDictionary.MARKDOWN_TO_RTF.__getattribute__('_value_')

    @commands.command(description=HelpDescription.LOG)
    async def log(self, ctx: commands.Context, channel: TextChannel) -> None:
        temporary_file_name: str = f"temporary_file_{channel.id}_{datetime.now().microsecond}"

        try:
            with open(temporary_file_name, mode="wb") as temporary_file:
                previous_message_author: Union[User, Member, None] = None
                current_message_text: str = ""
                temporary_file.write(r"{\rtf1\ansi\deff0{\fonttbl{\f0 Times New Roman;}}\f0\fs24".encode("utf-8"))

                async for message in channel.history(oldest_first=True):
                    # RTF? :
                    # https://interoperability.blob.core.windows.net/files/Archive_References/%5bMSFT-RTF%5d.pdf
                    # See also: RTF Pocket Guide

                    print(rf"{message.content}")
                    current_message_text = rf"{self.convert_markdown_to_rtf(message.content)}\line\line"
                    print(current_message_text)
                    temporary_file.write(current_message_text.encode("utf-8"))

                    if previous_message_author is None or message.author != previous_message_author:
                        previous_message_author = message.author

                    # Process:
                    # (1) Check the sender of the current message.
                    # (1a) If they're the same as the previous sender, continue.
                    # (1b) If they're not the same as the previous sender, denote them as the previous sender.
                    # (2) Format the message appropriately, removing any extraneous information or characters if necessary.
                    # Use the given information (options, character-user links) to do this accordingly.
                    # (3) Put the message in the file. Proceed.
                temporary_file.write("}".encode("utf-8"))

            with open(temporary_file_name, mode="rb") as temporary_file:
                # Upload the file to Discord.
                print(temporary_file.read())
                temporary_file.seek(0, 0)
                await ctx.send(StaticText.LOG_DEFAULT_TEXT, file=File(temporary_file, filename=f"log_{channel.name}.rtf"))
        finally:
            # Finally, destroy the file locally.
            os.remove(temporary_file_name)

        # to consider: text options?
        # to consider: how to relate users and characters; do I want to have a "general log" and an "RP log" option

    def convert_markdown_to_rtf(self, markdown_message: str) -> str:
        current_message: str = markdown_message
        for key, value in self.markdown_to_rtf.items():
            # We generate the patterns for the given key-value pair.
            group_pattern: str = rf"(?P<first>{key})(?P<between>.+)(?P<second>{key})"
            replace_pattern: str = rf"{{{value} \g<between>}}"

            # We iterate over the message to replace accordingly, stopping when no further matches are found.
            while (revised_message := re.sub(group_pattern, replace_pattern, current_message, 1)) != current_message:
                if revised_message:
                    current_message = revised_message

        if markdown_message == current_message:
            current_message = f"{{{current_message}}}"

        return current_message

# TODO: handle the issue of (2) line breaks in a message.