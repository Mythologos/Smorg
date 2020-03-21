from aenum import NamedConstant


class DiscordConstants(NamedConstant):
    MAX_MESSAGE_LENGTH = 2000


class ColorConstants(NamedConstant):
    ERROR_RED = 0xB80000
    HEAVENLY_YELLOW = 0xFFE066
    DEEP_BLUE = 0x001A66
    HOT_PINK = 0xFF3385
    NEUTRAL_ORANGE = 0xFF6600


class HelpDescriptions(NamedConstant):
    GOVERN = "This command tells Smorg what channel in which it should perform some task. " \
             "It takes a the type of channel (e.g. quotation, reminder), the channel's name, and, " \
             "if the channel has the same name as other channels, " \
             "the number of the instance of the channel as an argument."
    IMMORTALIZE = "This command embeds a quote and stores it for posterity's sake. " \
                  "It takes a quote and, optionally, an author as arguments."
    OBSERVE = "This command allows a Guild to change the prefix to which the bot will respond."
    QUOTE = "This command embeds a quote. " \
            "It takes a quote (in quotation marks) and, optionally, an author as arguments."
    REMIND = "This command signals a role at a certain time with a certain message. " \
             "It takes arguments in the order of role, time, and an optional message. " \
             "Time can be in terms of a twelve-hour or twenty-four-hour clock; " \
             "however, if it is the former, it must be in quotes with an A.M. or P.M. accompanying it. " \
             "Roles and messages consisting of multiple words should also be in quotes."
    ROLL = "This command rolls dice. It currently can handle rolls of the form xdy(k/d)z(!)(+/-)a(>/<)b, " \
           "where x, y, and z are nonnegative integers, and where a and b are integers. " \
           "Regular dice, drop-keep syntax, exploding dice, challenge dice, " \
           "and combinations of these are all supported. " \
           "Mathematical modifiers using + (addition), - (subtraction), * (multiplication), / (division), " \
           "^ (exponentiation), parentheses, floor(), ceiling(), abs(), and sqrt() are allowed. " \
           "Quoted, a description of what the roll was for may be included next. " \
           "The result is posted either in a set gamble channel or where the die was rolled."
    SUPPORT = "This command retrieves the menu below shown here."
    TRANSLATE = "This command translates text of one set of characters to another set of characters. " \
                "Current sets of characters include the Latin alphabet (alphabet) and Morse code (morse)."
    YOINK = "This command retrieves and displays a random stored quote."
