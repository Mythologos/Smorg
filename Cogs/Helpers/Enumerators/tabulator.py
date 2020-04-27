"""
...
"""

from __future__ import annotations

from aenum import Enum, NamedConstant
from math import floor, ceil, sqrt
from typing import Union


class ComparisonOperator(NamedConstant):
    """
    ...
    """
    LESS_THAN = -2
    LESS_THAN_OR_EQUAL_TO = -1
    EQUAL_TO = 0
    GREATER_THAN_OR_EQUAL_TO = 1
    GREATER_THAN = 2

    @staticmethod
    async def compare_by_value(comparison_value: int, item_a: int, item_b: int) -> bool:
        """
        ...

        :param int comparison_value:
        :param int item_a:
        :param int item_b:
        :return bool:
        """
        if comparison_value == ComparisonOperator.LESS_THAN:
            comparison_boolean = item_a < item_b
        elif comparison_value == ComparisonOperator.LESS_THAN_OR_EQUAL_TO:
            comparison_boolean = item_a <= item_b
        elif comparison_value == ComparisonOperator.EQUAL_TO:
            comparison_boolean = item_a == item_b
        elif comparison_value == ComparisonOperator.GREATER_THAN_OR_EQUAL_TO:
            comparison_boolean = item_a >= item_b
        else:
            comparison_boolean = item_a > item_b
        return comparison_boolean


class OperatorAssociativity(NamedConstant):
    """
    ...
    """
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class MathematicalOperator(Enum, init='value symbol precedence associativity'):
    """
    ...
    """
    ADDITION = (0, '+', 1, OperatorAssociativity.LEFT)
    SUBTRACTION = (1, '-', 1, OperatorAssociativity.LEFT)
    MULTIPLICATION = (2, '*', 2, OperatorAssociativity.LEFT)
    DIVISION = (3, '/', 2, OperatorAssociativity.LEFT)
    EXPONENTIATION = (4, '^', 3, OperatorAssociativity.RIGHT)

    @staticmethod
    async def get_by_symbol(given_symbol: str) -> MathematicalOperator:
        """
        ...

        :param str given_symbol:
        :return MathematicalOperator:
        """
        desired_operator: Union[MathematicalOperator, None] = None
        for operation in MathematicalOperator.__members__.values():
            if operation.symbol == given_symbol:
                desired_operator = operation
                break
        return desired_operator

    @staticmethod
    async def compare_precedence(symbol_one: MathematicalOperator, symbol_two: MathematicalOperator,
                                 comparison_value: int) -> bool:
        """
        ...

        :param MathematicalOperator symbol_one:
        :param MathematicalOperator symbol_two:
        :param int comparison_value:
        :return bool:
        """
        first_operator = await MathematicalOperator.get_by_symbol(symbol_one)
        second_operator = await MathematicalOperator.get_by_symbol(symbol_two)
        return await ComparisonOperator.compare_by_value(
            comparison_value, first_operator.precedence, second_operator.precedence
        )

    @staticmethod
    async def compare_associativity(symbol: MathematicalOperator, associativity: OperatorAssociativity) -> bool:
        """
        ...

        :param MathematicalOperator symbol:
        :param OperatorAssociativity associativity:
        :return bool:
        """
        associativity_indicator: bool = False
        relevant_operator = await MathematicalOperator.get_by_symbol(symbol)
        if relevant_operator.associativity == associativity:
            associativity_indicator = True
        return associativity_indicator

    @staticmethod
    async def evaluate_operator(associated_value: int, first_operand: Union[int, float],
                                second_operand: Union[int, float]) -> Union[int, float]:
        """
        ...

        :param int associated_value:
        :param Union[int, float] first_operand:
        :param Union[int, float] second_operand:
        :return Union[int, float]:
        """
        if associated_value == MathematicalOperator.ADDITION.value:
            evaluated_value = first_operand + second_operand
        elif associated_value == MathematicalOperator.SUBTRACTION.value:
            evaluated_value = first_operand - second_operand
        elif associated_value == MathematicalOperator.MULTIPLICATION.value:
            evaluated_value = first_operand * second_operand
        elif associated_value == MathematicalOperator.DIVISION.value:
            evaluated_value = first_operand / second_operand
        elif associated_value == MathematicalOperator.EXPONENTIATION.value:
            evaluated_value = first_operand**second_operand
        else:
            evaluated_value = 0
        return evaluated_value


class MathematicalFunction(Enum, init='value representation'):
    """
    ...
    """
    SQUARE_ROOT = (0, 'sqrt')
    FLOOR = (1, 'floor')
    CEILING = (2, 'ceiling')
    ABSOLUTE_VALUE = (3, 'abs')

    @staticmethod
    async def get_by_name(given_name: str) -> MathematicalFunction:
        """
        ...

        :param str given_name:
        :return MathematicalFunction:
        """
        desired_function = None
        for function in MathematicalFunction.__members__.values():
            if function.representation == given_name:
                desired_function = function
                break
        return desired_function

    @staticmethod
    async def evaluate_function(associated_value: int, first_operand: Union[int, float]) -> Union[int, float]:
        """
        ...

        :param int associated_value:
        :param Union[int, float] first_operand:
        :return Union[int, float]:
        """
        if associated_value == MathematicalFunction.SQUARE_ROOT.value:
            evaluated_value = sqrt(first_operand)
        elif associated_value == MathematicalFunction.FLOOR.value:
            evaluated_value = floor(first_operand)
        elif associated_value == MathematicalFunction.CEILING.value:
            evaluated_value = ceil(first_operand)
        elif associated_value == MathematicalFunction.ABSOLUTE_VALUE.value:
            evaluated_value = abs(first_operand)
        else:
            evaluated_value = 0
        return evaluated_value
