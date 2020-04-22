from aenum import Enum, NamedConstant


class MatchContent(NamedConstant):
    DIE_ROLL = 0
    REGULAR_OPERATOR = 1
    GROUPING_OPERATOR = 2
    FUNCTION = 3
    CONSTANT = 4


class RollMechanic(Enum, init='representation value_range description'):
    NUMBER_OF_DICE = ("x", "This value can be any positive integer.",
                      "This value represents the number of dice that are rolled.")
    ROLL_NOTIFIER = ("d", "This symbol can be 'd' or 'D'.", "This symbol indicates that dice are being rolled.")
    DIE_SIZE = ("y", "This value can be any positive integer",
                "This value represents the size of the dice that are rolled.")
    DROP_NOTIFIER = ("d", "This symbol can be 'd' or 'D'.",
                     "This symbol indicates that a certain number of the dice with the lowest rolls will not count.")
    KEEP_NOTIFIER = ("k", "This symbol can be 'k' or 'K'.",
                     "This symbol indicates that a certain number of the dice with the highest rolls will count.")
    DROP_KEEP_SIZE = ("z", "This value can be any positive integer.",
                      "This value represents the number of dice that'll be kept or dropped.")
    EXPLOSION_NOTIFIER = ("!", "This symbol can only be '!'.",
                          "This symbol indicates that dice that roll the maximum value will roll an additional die.")
    CHALLENGE_SYMBOL = (">", "This symbol can be '>' or '<'.",
                        "This symbol indicates that a challenge die system will be used. "
                        "If '>' is used and the value rolled is greater than or equal to the size of the challenge, "
                        "a success is gained. The '<' sign represents a 'less-than-or-equal-to' symbol.")
    CHALLENGE_SIZE = ("a", "This value can be any integer.",
                      "This value is the number that the dice must meet, exceed, or fall below in order to succeed.")
