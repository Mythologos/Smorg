from aenum import Enum
import math


class ShuntComparison(Enum):
    LESS_THAN = -2
    LESS_THAN_OR_EQUAL_TO = -1
    EQUAL_TO = 0
    GREATER_THAN_OR_EQUAL_TO = 1
    GREATER_THAN = 2

    @staticmethod
    async def compare_by_value(ctx, comparison_value, item_a, item_b):
        comparison_boolean: bool = False
        if comparison_value == ShuntComparison.LESS_THAN.value:
            comparison_boolean = item_a < item_b
        elif comparison_value == ShuntComparison.LESS_THAN_OR_EQUAL_TO.value:
            comparison_boolean = item_a <= item_b
        elif comparison_value == ShuntComparison.EQUAL_TO.value:
            comparison_boolean = item_a == item_b
        elif comparison_value == ShuntComparison.GREATER_THAN_OR_EQUAL_TO.value:
            comparison_boolean = item_a >= item_b
        elif comparison_value == ShuntComparison.GREATER_THAN.value:
            comparison_boolean = item_a > item_b
        else:
            await ctx.send("Error: unknown comparison value. Please try again!")
        return comparison_boolean


class ShuntAssociativity(Enum, init='direction'):
    LEFT = ('left',)
    RIGHT = ('right',)
    NONE = ('none',)


class ShuntOperator(Enum, init='value symbol precedence associativity'):
    ADDITION = (0, '+', 1, ShuntAssociativity.LEFT)
    SUBTRACTION = (1, '-', 1, ShuntAssociativity.LEFT)
    MULTIPLICATION = (2, '*', 2, ShuntAssociativity.LEFT)
    DIVISION = (3, '/', 2, ShuntAssociativity.LEFT)
    EXPONENTIATION = (4, '^', 3, ShuntAssociativity.RIGHT)

    @staticmethod
    async def get_by_symbol(ctx, given_symbol):
        desired_operator = None
        for operation in ShuntOperator:
            if operation.symbol == given_symbol:
                desired_operator = operation
                break
        if not desired_operator:
            await ctx.send("Error: Corresponding operation for operator " + given_symbol +
                           " not found. Please try again!")
        else:
            return desired_operator

    @staticmethod
    async def compare_precedence(ctx, symbol_one: str, symbol_two: str, comparison_value: ShuntComparison) -> bool:
        first_operator = await ShuntOperator.get_by_symbol(ctx, symbol_one)
        second_operator = await ShuntOperator.get_by_symbol(ctx, symbol_two)
        precedence_boolean: bool = await ShuntComparison.compare_by_value(ctx, comparison_value.value,
                                                                          first_operator.precedence,
                                                                          second_operator.precedence)
        return precedence_boolean

    @staticmethod
    async def compare_associativity(ctx, symbol, associativity):
        associativity_indicator: bool = False
        relevant_operator = await ShuntOperator.get_by_symbol(ctx, symbol)
        if relevant_operator.associativity == associativity:
            associativity_indicator = True
        return associativity_indicator

    @staticmethod
    async def function_evaluator(associated_value, first_operand, second_operand):
        evaluated_value = 0
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
        return evaluated_value


class ShuntFunction(Enum, init='value representation'):
    SQUARE_ROOT = (0, 'sqrt')
    FLOOR = (1, 'floor')
    CEILING = (2, 'ceiling')
    ABSOLUTE_VALUE = (3, 'abs')

    @staticmethod
    async def get_by_name(ctx, given_name):
        desired_function = None
        for function in ShuntFunction:
            if function.representation == given_name:
                desired_function = function
                break
        if not desired_function:
            await ctx.send("Error: Corresponding functionality for function " + given_name +
                           " not found. Please try again!")
        else:
            return desired_function

    @staticmethod
    async def function_evaluator(associated_value, first_operand):
        evaluated_value: float = 0
        if associated_value == ShuntFunction.SQUARE_ROOT.value:
            evaluated_value = math.sqrt(first_operand)
        elif associated_value == ShuntFunction.FLOOR.value:
            evaluated_value = math.floor(first_operand)
        elif associated_value == ShuntFunction.CEILING.value:
            evaluated_value = math.ceil(first_operand)
        elif associated_value == ShuntFunction.ABSOLUTE_VALUE.value:
            evaluated_value = abs(first_operand)
        return evaluated_value
