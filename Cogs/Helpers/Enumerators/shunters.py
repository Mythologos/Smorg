# TODO: documentation
# TODO: fix IDE not reading some items correctly, if possible
# TODO: perhaps alter the names here, as much of this could be used for general mathematics?

from __future__ import annotations

import math

from aenum import Enum, NamedConstant


class ShuntComparison(NamedConstant):
    LESS_THAN = -2
    LESS_THAN_OR_EQUAL_TO = -1
    EQUAL_TO = 0
    GREATER_THAN_OR_EQUAL_TO = 1
    GREATER_THAN = 2

    @staticmethod
    async def compare_by_value(comparison_value: int, item_a: int, item_b: int) -> bool:
        if comparison_value == ShuntComparison.LESS_THAN:
            comparison_boolean = item_a < item_b
        elif comparison_value == ShuntComparison.LESS_THAN_OR_EQUAL_TO:
            comparison_boolean = item_a <= item_b
        elif comparison_value == ShuntComparison.EQUAL_TO:
            comparison_boolean = item_a == item_b
        elif comparison_value == ShuntComparison.GREATER_THAN_OR_EQUAL_TO:
            comparison_boolean = item_a >= item_b
        else:
            comparison_boolean = item_a > item_b
        return comparison_boolean


class ShuntAssociativity(NamedConstant):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class ShuntOperator(Enum, init='value symbol precedence associativity'):
    ADDITION = (0, '+', 1, ShuntAssociativity.LEFT)
    SUBTRACTION = (1, '-', 1, ShuntAssociativity.LEFT)
    MULTIPLICATION = (2, '*', 2, ShuntAssociativity.LEFT)
    DIVISION = (3, '/', 2, ShuntAssociativity.LEFT)
    EXPONENTIATION = (4, '^', 3, ShuntAssociativity.RIGHT)

    @staticmethod
    async def get_by_symbol(given_symbol: str) -> ShuntOperator:
        desired_operator = None
        for operation in ShuntOperator:
            if operation.symbol == given_symbol:
                desired_operator = operation
                break
        return desired_operator

    @staticmethod
    async def compare_precedence(symbol_one: ShuntOperator, symbol_two: ShuntOperator, comparison_value: int) -> bool:
        first_operator = await ShuntOperator.get_by_symbol(symbol_one)
        second_operator = await ShuntOperator.get_by_symbol(symbol_two)
        return await ShuntComparison.compare_by_value(comparison_value,
                                                      first_operator.precedence,
                                                      second_operator.precedence)

    @staticmethod
    async def compare_associativity(symbol, associativity):
        associativity_indicator: bool = False
        relevant_operator = await ShuntOperator.get_by_symbol(symbol)
        if relevant_operator.associativity == associativity:
            associativity_indicator = True
        return associativity_indicator

    @staticmethod
    async def evaluate_operator(associated_value, first_operand, second_operand):
        if associated_value == ShuntOperator.ADDITION.value:
            evaluated_value = first_operand + second_operand
        elif associated_value == ShuntOperator.SUBTRACTION.value:
            evaluated_value = first_operand - second_operand
        elif associated_value == ShuntOperator.MULTIPLICATION.value:
            evaluated_value = first_operand * second_operand
        elif associated_value == ShuntOperator.DIVISION.value:
            evaluated_value = first_operand / second_operand
        elif associated_value == ShuntOperator.EXPONENTIATION.value:
            evaluated_value = first_operand**second_operand
        else:
            evaluated_value = 0
        return evaluated_value


class ShuntFunction(Enum, init='value representation'):
    SQUARE_ROOT = (0, 'sqrt')
    FLOOR = (1, 'floor')
    CEILING = (2, 'ceiling')
    ABSOLUTE_VALUE = (3, 'abs')

    @staticmethod
    async def get_by_name(given_name):
        desired_function = None
        for function in ShuntFunction:
            if function.representation == given_name:
                desired_function = function
                break
        return desired_function

    @staticmethod
    async def evaluate_function(associated_value, first_operand):
        if associated_value == ShuntFunction.SQUARE_ROOT.value:
            evaluated_value = math.sqrt(first_operand)
        elif associated_value == ShuntFunction.FLOOR.value:
            evaluated_value = math.floor(first_operand)
        elif associated_value == ShuntFunction.CEILING.value:
            evaluated_value = math.ceil(first_operand)
        elif associated_value == ShuntFunction.ABSOLUTE_VALUE.value:
            evaluated_value = abs(first_operand)
        else:
            evaluated_value = 0
        return evaluated_value
