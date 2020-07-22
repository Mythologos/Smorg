"""
This module contains the YardShunter class. It implements the shunting yard algorithm, created by
Dr. Edsger Dijkstra, for use in Smorg.

Shunting Yard algorithm: https://en.wikipedia.org/wiki/Shunting-yard_algorithm
"""

from typing import Union

from .exceptioner import DuplicateOperator, ImproperFunction, MissingParenthesis, InvalidSequence
from .Enumerators.tabulator import ComparisonOperator, MathematicalFunction, MathematicalOperator, OperatorAssociativity


class YardShunter:
    """
    This class revolves around the implementation of the shunting yard algorithm.
    To perform this algorithm multiple times throughout Smorg's lifetime, it assures that its stacks
    are empty by using the flush_stacks() function. Input is simplified and converted appropriately
    in the consolidate_tokens() function. It is processed by the core algorithm in the process_input() function.
    Finally, the results are evaluated in the evaluate_input() function.
    """
    def __init__(self):
        self.operator_stack: list = []
        self.output_queue: list = []
        self.current_functions: list = [member.representation for name, member
                                        in MathematicalFunction.__members__.items()]
        self.current_operators: list = [member.symbol for name, member in MathematicalOperator.__members__.items()]
        self.grouping_operators: tuple = ('(', ')')

    async def shunt_yard(self, flat_tokens: list) -> Union[float, int]:
        """
        This method is the main method for the full process of the shunting yard algorithm.
        it performs all of the steps necessary for the shunting yard algorithm in their appropriate order,
        using the flush_stacks() function to assure that the function can be performed multiple times
        with different inputs throughout Smorg's lifetime.

        :param list flat_tokens: a one-dimensional list of numerical, symbolic, and functional tokens
        accepted by Smorg's parsing algorithms (e.g. those in gambler).
        :return Union[float, int]: the value resulting from the mathematical calculations designated by the tokens.
        """
        await self.flush_stacks()
        complete_tokens: list = await self.consolidate_tokens(flat_tokens)
        await self.process_input(complete_tokens)
        final_result: Union[float, int] = await self.evaluate_input()
        return final_result

    async def flush_stacks(self) -> None:
        """
        This function clears operator_stack and output_queue so that future uses of yard_shunter aren't impacted
        by previous uses.
        """
        self.operator_stack.clear()
        self.output_queue.clear()

    async def consolidate_tokens(self, flattened_tokens: list) -> list:
        """
        This method converts numerical tokens to their proper types,
        converts numbers to their negative counterparts based on the placement of '-' signs,
        and helps for the algorithm to catch more specific kinds of errors.

        :param list flattened_tokens: a one-dimensional collection of mathematical tokens.
        :return list: a collection of tokens with numbers converted to integers
        and negative numbers more properly designated as such.
        """
        index: int = 0
        previous_is_operator: bool = False
        while index < len(flattened_tokens):
            current_token = flattened_tokens[index]
            next_token = flattened_tokens[index + 1] if (index + 1 < len(flattened_tokens)) else None
            if current_token.isdigit():
                flattened_tokens[index] = int(flattened_tokens[index])
                previous_is_operator = False
            elif current_token in self.current_operators:
                if current_token == '-' and next_token:  # this section helps to handle negative numbers vs. subtraction
                    if next_token.isdigit():
                        flattened_tokens[index] = int(current_token + next_token)
                        del flattened_tokens[index + 1], next_token
                    elif next_token not in self.current_operators:
                        flattened_tokens[index] = -1
                        flattened_tokens.insert(1, '*')
                    else:
                        raise DuplicateOperator
                elif not previous_is_operator:
                    previous_is_operator = True
                else:
                    raise DuplicateOperator
            elif current_token in self.current_functions:
                if next_token in self.grouping_operators:
                    index += 1
                else:
                    raise ImproperFunction
            index += 1
        return flattened_tokens

    async def process_input(self, complete_tokens: list) -> None:
        """
        This method performs the shunting-yard algorithm. This implementation used the pseudo-code written
        at the following location to build this algorithm:
        https://en.wikipedia.org/wiki/Shunting-yard_algorithm#The_algorithm_in_detail

        :param list complete_tokens: a list of tokens containing valid operators, appropriately-typed numbers,
        and functions.
        """
        index: int = 0
        while index < len(complete_tokens):
            if isinstance(complete_tokens[index], int):
                self.output_queue.append(int(complete_tokens[index]))
            elif complete_tokens[index] in self.current_functions:
                self.operator_stack.insert(0, complete_tokens[index])
            elif complete_tokens[index] in self.current_operators:
                while self.operator_stack and self.operator_stack[0] != '(':
                    last_was_function = self.operator_stack[0] in self.current_functions
                    current_has_precedence = await MathematicalOperator.compare_precedence(
                        self.operator_stack[0], complete_tokens[index], ComparisonOperator.GREATER_THAN
                    )
                    last_equal_precedence = await MathematicalOperator.compare_precedence(
                        self.operator_stack[0], complete_tokens[index], ComparisonOperator.EQUAL_TO
                    )
                    last_left_associative = await MathematicalOperator.compare_associativity(
                        self.operator_stack[0], OperatorAssociativity.LEFT
                    )
                    if last_was_function or current_has_precedence or (last_equal_precedence and last_left_associative):
                        self.output_queue.append(self.operator_stack.pop(0))
                    else:
                        break
                self.operator_stack.insert(0, complete_tokens[index])
            elif complete_tokens[index] == '(':
                self.operator_stack.insert(0, complete_tokens[index])
            elif complete_tokens[index] == ')':
                while self.operator_stack and self.operator_stack[0] != '(':
                    self.output_queue.append(self.operator_stack.pop(0))
                if self.operator_stack[0] == '(':
                    self.operator_stack.pop(0)
                else:
                    raise MissingParenthesis
            index += 1
        else:
            while self.operator_stack:
                if self.operator_stack[0] in self.grouping_operators:
                    raise MissingParenthesis
                else:
                    self.output_queue.append(self.operator_stack.pop(0))

    async def evaluate_input(self) -> Union[float, int]:
        """
        This method evaluates the input produced by the shunting yard algorithm,
        calculating a final result if the input is, in fact, valid.

        :return Union[float, int]: the final result of the calculations produced by the shunting yard algorithm.
        """
        output_stack: list = []
        for output in self.output_queue:
            if output in self.current_operators:
                if len(output_stack) > 1:  # currently only handles two-operand operators
                    second_operand: int = output_stack.pop(0)
                    first_operand: int = output_stack.pop(0)
                    relevant_operator: MathematicalOperator = await MathematicalOperator.get_by_symbol(output)
                    operation_result: Union[int, float] = await MathematicalOperator.evaluate_operator(
                        relevant_operator.value, first_operand, second_operand
                    )
                    output_stack.insert(0, operation_result)
                else:
                    raise InvalidSequence
            elif output in self.current_functions:
                if output_stack:
                    first_operand: int = output_stack.pop(0)  # currently only hands one-operand functions
                    relevant_function: MathematicalFunction = await MathematicalFunction.get_by_name(output)
                    operation_result: Union[int, float] = await MathematicalFunction.evaluate_function(
                        relevant_function.value, first_operand
                    )
                    output_stack.insert(0, operation_result)
                else:
                    raise InvalidSequence
            else:
                output_stack.insert(0, output)
        return output_stack[0]
