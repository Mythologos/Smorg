from Cogs.Helpers.exceptioner import DuplicateOperator, ImproperFunction, MissingParenthesis, InvalidSequence
from Cogs.Helpers.Enumerators.tabulator import ComparisonOperator, MathematicalFunction, MathematicalOperator,\
    OperatorAssociativity

from typing import Union


class YardShunter:
    def __init__(self):
        self.operator_stack: list = []
        self.output_queue: list = []
        self.current_functions: list = [member.representation for name, member
                                        in MathematicalFunction.__members__.items()]
        self.current_operators: list = [member.symbol for name, member in MathematicalOperator.__members__.items()]
        self.grouping_operators: tuple = ('(', ')')

    async def shunt_yard(self, flat_tokens: list) -> Union[float, int]:
        await self.flush_stacks()
        complete_tokens: list = await self.consolidate_tokens(flat_tokens)
        await self.process_input(complete_tokens)
        final_result: Union[float, int] = await self.evaluate_input()
        return final_result

    async def flush_stacks(self):
        self.operator_stack.clear()
        self.output_queue.clear()

    async def consolidate_tokens(self, flattened_tokens: list) -> list:
        index: int = 0
        previous_is_operator: bool = False
        while index < len(flattened_tokens):
            current_token = flattened_tokens[index]
            next_token = flattened_tokens[index + 1] if (index + 1 < len(flattened_tokens)) else None
            if current_token.isdigit():
                flattened_tokens[index] = int(flattened_tokens[index])
                previous_is_operator = False
            elif current_token in self.current_operators:
                if current_token == '-' and next_token:
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
        output_stack: list = []
        for output in self.output_queue:
            if output in self.current_operators:
                if len(output_stack) > 1:
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
                    first_operand: int = output_stack.pop(0)
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
