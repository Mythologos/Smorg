from aenum import Enum


class RollComponent(Enum):
    NUMBER_OF_DICE = 0
    DIE_SIZE = 1
    DROP_KEEP_VALUE = 2
    EXPLOSION_VALUE = 3
    OVERALL_MODIFIER = 4
    CHALLENGE_VALUE = 5


class RollParseResult(Enum):
    NUMBER_OF_DICE = 0
    DIE_SIZE = 1
    DROP_KEEP_VALUE = 2
    DROP_KEEP_INDICATOR = 3
    EXPLOSION_BOOLEAN = 4
    OVERALL_MODIFIER = 5
    CHALLENGE_VALUE = 6
    CHALLENGE_INDICATOR = 7


class RollResult(Enum):
    FINAL_RESULT = 0
    UNSORTED_RESULTS = 1
    INDIVIDUAL_RESULTS = 2


# Note: challenge dice systems use > and < but mean >= and <= generally,
# So this class uses the below in that way.
class ComparisonIndicator(Enum):
    LESS_THAN = -1
    NO_COMPARISON = 0
    GREATER_THAN = 1


# Note: drop and keep may have slightly different behaviors depending on the circumstances.
# So a boolean isn't enough.
class DropKeepIndicator(Enum):
    NONE = 0
    DROP = 1
    KEEP = 2
