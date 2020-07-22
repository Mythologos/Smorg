"""
This module consists of a number of classes that represent basic mathematical constructs.
ComparisonOperator deals with equality and inequality.
OperatorAssociativity manages associativity for operators and is mainly a special component of actual operators.
MathematicalOperator concerns actual mathematical operators such as addition ('+') and subtraction ('-').
MathematicalFunction considers those mathematical constructs that are not often expressed via symbols
and usually take one argument, such as 'floor()' or 'ceiling()'.
"""

from __future__ import annotations

from aenum import Enum, NamedConstant
from math import floor, ceil, sqrt
from typing import Union

from ..exceptioner import InvalidComparison, InvalidFunction, InvalidOperator


class ComparisonOperator(NamedConstant):
    """
    This class contains constants to represent comparative operators.
    """
    LESS_THAN = -2
    LESS_THAN_OR_EQUAL_TO = -1
    EQUAL_TO = 0
    GREATER_THAN_OR_EQUAL_TO = 1
    GREATER_THAN = 2

    @staticmethod
    async def compare_by_value(comparison_value: int, item_a: Union[int, float],
                               item_b: Union[int, float]) -> bool:
        """
        This method, based on the comparison_value given, compares two values.

        :param int comparison_value: the value that designates what kind of comparison to perform.
        :param Union[int, float] item_a: the first value to be compared.
        :param Union[int, float] item_b: the second value to be compared.
        :return bool: a result pertinent to the type of comparison performed.
        """
        if comparison_value == ComparisonOperator.LESS_THAN:
            comparison_boolean = item_a < item_b
        elif comparison_value == ComparisonOperator.LESS_THAN_OR_EQUAL_TO:
            comparison_boolean = item_a <= item_b
        elif comparison_value == ComparisonOperator.EQUAL_TO:
            comparison_boolean = item_a == item_b
        elif comparison_value == ComparisonOperator.GREATER_THAN_OR_EQUAL_TO:
            comparison_boolean = item_a >= item_b
        elif comparison_value == ComparisonOperator.GREATER_THAN:
            comparison_boolean = item_a > item_b
        else:
            raise InvalidComparison
        return comparison_boolean


class OperatorAssociativity(NamedConstant):
    """
    This class holds constants that concern the associativity of operators.
    """
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class MathematicalOperator(Enum, init='value symbol precedence associativity'):
    """
    This enumeration concerns mathematical operators for essential symbolic mathematical calculations.
    It has four components: the value of the Enum, the symbol it represents,
    the precedence it has when compared to other operators, and the type of associativity it bears.
    """
    ADDITION = (0, '+', 1, OperatorAssociativity.LEFT)
    SUBTRACTION = (1, '-', 1, OperatorAssociativity.LEFT)
    MULTIPLICATION = (2, '*', 2, OperatorAssociativity.LEFT)
    DIVISION = (3, '/', 2, OperatorAssociativity.LEFT)
    EXPONENTIATION = (4, '^', 3, OperatorAssociativity.RIGHT)

    @staticmethod
    async def get_by_symbol(given_symbol: str) -> MathematicalOperator:
        """
        This method retrieves an operator from MathematicalOperator based on its symbol.

        :param str given_symbol: the symbol which the desired MathematicalOperator should have.
        :return MathematicalOperator: the operator corresponding to the given symbol.
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
        This method returns a boolean based on the comparison of two operators' precedences and a comparison value.

        :param MathematicalOperator symbol_one: the first operator whose precedence will be compared.
        :param MathematicalOperator symbol_two: the second operator whose precedence will be compared.
        :param int comparison_value: the indicator of how the precedences will be compared.
        :return bool: the result of the comparison between the two symbols' precedence.
        """
        first_operator = await MathematicalOperator.get_by_symbol(symbol_one)
        second_operator = await MathematicalOperator.get_by_symbol(symbol_two)
        return await ComparisonOperator.compare_by_value(
            comparison_value, first_operator.precedence, second_operator.precedence
        )

    @staticmethod
    async def compare_associativity(symbol: MathematicalOperator, associativity: OperatorAssociativity) -> bool:
        """
        This method determines whether a given symbol has a given associativity.

        :param MathematicalOperator symbol: a given symbol whose associativity will be compared with the given
        associativity object.
        :param OperatorAssociativity associativity: an associativity to which the given symbol's associativity
        will be compared.
        :return bool: True if the symbol's MathematicalOperator's associativity is the same as the given associativity;
        False, otherwise.
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
        This method performs some mathematical operation, based on the associated_value given,
        with the given operands. It returns the result of this calculation.

        :param int associated_value: the value belonging to a MathematicalOperator that indicates which operation
        should be performed on the operands.
        :param Union[int, float] first_operand: the first operator to be used in some calculation.
        :param Union[int, float] second_operand: the second operator to be used in some calculation.
        :return Union[int, float]: the result of the mathematical calculation.
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
            raise InvalidOperator
        return evaluated_value


class MathematicalFunction(Enum, init='value representation'):
    """
    This enumeration concerns mathematical functions and the way in which they are represented.
    """
    SQUARE_ROOT = (0, 'sqrt')
    FLOOR = (1, 'floor')
    CEILING = (2, 'ceiling')
    ABSOLUTE_VALUE = (3, 'abs')

    @staticmethod
    async def get_by_name(given_name: str) -> MathematicalFunction:
        """
        This method retrieves an operator from MathematicalFunction based on its name.

        :param str given_name: the name which the desired MathematicalFunction should have.
        :return MathematicalFunction: the function corresponding to the given name.
        """
        desired_function = None
        for function in MathematicalFunction.__members__.values():
            if function.representation == given_name:
                desired_function = function
                break
        return desired_function

    @staticmethod
    async def evaluate_function(associated_value: int, first_input: Union[int, float]) -> Union[int, float]:
        """
        This method performs some mathematical function, based on the associated_value given,
        with the given operand. It returns the result of this calculation.

        :param int associated_value: the value belonging to a MathematicalFunction that indicates which function
        will take first_input as its input.
        :param Union[int, float] first_input: the operator to be used in some calculation.
        :return Union[int, float]: the result of the mathematical calculation.
        """
        if associated_value == MathematicalFunction.SQUARE_ROOT.value:
            evaluated_value = sqrt(first_input)
        elif associated_value == MathematicalFunction.FLOOR.value:
            evaluated_value = floor(first_input)
        elif associated_value == MathematicalFunction.CEILING.value:
            evaluated_value = ceil(first_input)
        elif associated_value == MathematicalFunction.ABSOLUTE_VALUE.value:
            evaluated_value = abs(first_input)
        else:
            raise InvalidFunction
        return evaluated_value
