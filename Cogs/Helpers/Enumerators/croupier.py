from aenum import Enum, NamedConstant


class MessageConstant(NamedConstant):
    DEFAULT_MSG_CHARACTERS = 47


class MatchContent(Enum):
    DIE_ROLL = 0
    REGULAR_OPERATOR = 1
    GROUPING_OPERATOR = 2
    FUNCTION = 3
    CONSTANT = 4
