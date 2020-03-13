from aenum import Enum, NamedConstant


class MessageConstants(NamedConstant):
    DEFAULT_MSG_CHARACTERS = 47
    DISCORD_MSG_LENGTH = 2000


class MatchContents(Enum):
    DIE_ROLL = 0
    REGULAR_OPERATOR = 1
    GROUPING_OPERATOR = 2
    FUNCTION = 3
    CONSTANT = 4
