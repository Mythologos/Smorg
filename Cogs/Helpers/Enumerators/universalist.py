# TODO: documentation...

from aenum import NamedConstant


class ColorConstant(NamedConstant):
    ERROR_RED = 0xB80000
    HEAVENLY_YELLOW = 0xFFE066
    DEEP_BLUE = 0x001A66
    HOT_PINK = 0xFF3385
    NEUTRAL_ORANGE = 0xFF6600
    VIBRANT_PURPLE = 0xA901DB
    CALM_GREEN = 0x0CCC3F


class DiscordConstant(NamedConstant):
    MAX_MEMBER_NAME_LENGTH = 32
    MAX_ROLE_LENGTH = 100
    MAX_MESSAGE_LENGTH = 2000
    MAX_EMBED_TITLE = 256
    MAX_EMBED_DESCRIPTION = 2048
    MAX_EMBED_FIELDS = 25
    MAX_EMBED_FIELD_NAME = 256
    MAX_EMBED_FIELD_VALUE = 1024
    MAX_EMBED_FOOTER = 2048
    MAX_EMBED_AUTHOR = 256


class HelpDescription(NamedConstant):
    DISPLAY = "This command, when combined with various subcommands, relates information about Smorg's capabilities " \
              "and its current state. " \
              "Current subcommands include dice, functions, operators, quotes, reminders, and zones."
    FORGET = "This command allows someone to delete a reminder. To do so, it accepts arguments of a role and a time. " \
             "It deletes a reminder corresponding to that role and time."
    GOVERN = "This command tells Smorg what channel in which it should perform some task. " \
             "It takes a the type of channel (e.g. quotation, reminder), the channel's name, and, " \
             "if the channel has the same name as other channels, " \
             "the number of the instance of the channel as an argument."
    IMMORTALIZE = "This command embeds a quote and stores it for posterity's sake. " \
                  "It takes a quote and, optionally, an author as arguments."
    OBSERVE = "This command allows a Guild to change the prefix to which the bot will respond."
    PURGE = "This command deletes a specified number of messages prior to the given command."
    QUOTE = "This command embeds a quote. It takes a quote and, optionally, an author as arguments. " \
            "The author can be a mention or regular text."
    REMIND = "This command signals a role at a certain time with a certain message. " \
             "It takes arguments in the order of role, time, and an optional message. " \
             "Time can be in terms of a twelve-hour or twenty-four-hour clock. " \
             "Dates and times must be given as follows: '[time] [time zone]; [day] [month] [year]'. " \
             "Messages consisting of multiple words should be in quotes."
    ROLL = "This command rolls dice. See various display subcommand tables for die and modifier options. " \
           "Next, if you want the roll to be sent to certain members rather than publicly displayed in a channel, " \
           "you may mention those members that you want to receive the roll. " \
           "The roller is not automatically included. " \
           "You may also provide a description of the roll's purpose after these items. "
    REVISE = "This command allows someone to edit a reminder's description. " \
             "To do so, it accepts arguments of a role, a time, and a new description."
    SUPPORT = "This command retrieves a help menu that lists information about all commands that Smorg supports."
    TRANSLATE = "This command translates text of one set of characters to another set of characters. " \
                "Current sets of characters include the Latin alphabet (alphabet) and Morse code (morse)."
    YOINK = "This command retrieves and displays a random stored quote."


class MessageConstant(NamedConstant):
    NOT_FOUND_INDEX = -1
    CONDENSE_CHARACTERS = 12
    DIE_ROLL_CHARACTERS = 48
    DIE_TRUNCATION_CHARACTERS = 10


class StaticText(NamedConstant):
    ERROR_ON_READY_TEXT = "Smorg is online, but your Guild currently has no text channels. " \
                          "Please remove Smorg from your Guild and add Smorg back once there is a text channel."
    NEW_ON_READY_TEXT = "Hello! Smorg is online! To view commands, please use the 'help' command " \
                        "with the appropriate prefix. If this is your first time using this bot, '.' is your prefix."
    REGULAR_ON_READY_TEXT = "Smorg is online!"
    GOVERN_GAMBLE_TEXT = "Congrats! You have successfully changed where you let dice fly."
    GOVERN_QUOTATION_TEXT = "Congrats! You have successfully changed where I engrave your greatest sayings."
    GOVERN_REMINDER_TEXT = "Congrats! You have successfully changed where I blare your noisiest remembrances."
    REMINDER_NOTIFICATION = "Your reminder has been successfully processed! It'll be sent at the specified time."
    REVISED_REMINDER_NOTIFICATION = "Your reminder revision has been successfully processed!"
    FORGOTTEN_REMINDER_NOTIFICATION = "Your reminder deletion has been successfully processed!"
    LIST_TRUNCATION_TEXT = "[...]"
