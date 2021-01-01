import os
import re

from datetime import datetime
from typing import List, Union

from discord import File, Member, TextChannel, User
from discord.ext import commands
from discord.ext.commands import Greedy, TooManyArguments

from .Helpers.Enumerators.universalist import HelpDescription, StaticText
from .Helpers.Enumerators.polyglot import FormatDictionary


class Logger(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        #  See the encoder class for a discussion of this idiom.
        self.markdown_to_rtf = FormatDictionary.MARKDOWN_TO_RTF.__getattribute__('_value_')

    @commands.command(description=HelpDescription.LOG)
    async def log(self, ctx: commands.Context, channel: TextChannel, member_list: Greedy[Member],
                  *nickname_list) -> None:
        if len(member_list) != len(nickname_list):
            raise TooManyArguments

        # TODO: make custom exceptions to support this functionality
        # if len(member_list) > len(nickname_list):
            # raise TooManyArguments(message="There are more members given than nicknames.")
        # elif len(nickname_list) > len(member_list):
            # raise TooManyArguments(message="There are more nicknames given than members.")

        temporary_file_name: str = f"temporary_file_{channel.id}_{datetime.now().microsecond}"

        # The try-finally block doesn't do error handling, but it assures that if there is an error,
        # the temporary file created is always deleted.
        try:
            with open(temporary_file_name, mode="wb") as temporary_file:
                current_message_author: Union[User, Member, None] = None
                temporary_file.write(r"{\rtf1\ansi\deff0{\fonttbl{\f0 Times New Roman;}}\f0\fs24".encode("utf-8"))

                async for message in channel.history(oldest_first=True):
                    current_message_text: str = ""
                    # RTF: https://interoperability.blob.core.windows.net/files/Archive_References/%5bMSFT-RTF%5d.pdf
                    # See also: RTF Pocket Guide

                    # Logger sets up a post-message divider when the message is not first and
                    # the message is by a different author than the previous existing author.
                    if current_message_author and current_message_author != message.author:
                        temporary_file.write(r"{{\pard\qc ---\line\par}}".encode("utf-8"))

                    # Logger adds text denoting the author if the author is new.
                    if current_message_author is None or message.author != current_message_author:
                        current_message_author = message.author
                        current_message_text = rf"{{\b {self.convert_author_to_nickname(current_message_author, member_list, nickname_list)}}}: "

                    current_message_text += rf"{{\pard\ql {self.convert_markdown_to_rtf(message.content)}\line\par}}"
                    print(current_message_text)
                    temporary_file.write(current_message_text.encode("utf-8"))

                temporary_file.write("}".encode("utf-8"))

            with open(temporary_file_name, mode="rb") as temporary_file:
                # Upload the file to Discord.
                print(temporary_file.read())
                temporary_file.seek(0, 0)
                await ctx.send(StaticText.LOG_DEFAULT_TEXT,
                               file=File(temporary_file, filename=f"log_{channel.name}.rtf"))
        finally:
            # Finally, destroy the file locally.
            os.remove(temporary_file_name)

        # to consider: text options?
        # to consider: how to relate users and characters; do I want to have a "general log" and an "RP log" option

    def convert_markdown_to_rtf(self, markdown_message: str) -> str:
        current_message: str = markdown_message.replace("\n", "\\line ")
        for key, value in self.markdown_to_rtf.items():
            # We generate the patterns for the given key-value pair.
            group_pattern: str = rf"(?P<first>{key})(?P<between>.+?)(?P<second>{key})"
            replace_pattern: str = rf"{{{value} \g<between>}}"

            # We iterate over the message to replace accordingly, stopping when no further matches are found.
            while (revised_message := re.sub(group_pattern, replace_pattern, current_message, 1)) != current_message:
                if revised_message:
                    current_message = revised_message

        return current_message

    @staticmethod
    def convert_author_to_nickname(current_message_author: Member, member_list: List[Member], nickname_list) -> str:
        found_nickname: str = current_message_author.name
        for index, member in enumerate(member_list):
            if current_message_author == member:
                found_nickname = nickname_list[index]
        return found_nickname

