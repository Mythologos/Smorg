from Cogs.Helpers.exceptioner import DuplicateOperator, ImproperFunction, MissingParenthesis
from Cogs.Helpers.Enumerators.shunters import ShuntAssociativity, ShuntFunction, ShuntOperator, ShuntComparison

from typing import Union


class YardShunter:
    def __init__(self):
        self.operator_stack: list = []
        self.output_queue: list = []
        self.current_functions: list = []
        for name, member in ShuntFunction.__members__.items():
            self.current_functions.append(member.representation)
        self.current_operators: list = []
        for name, member in ShuntOperator.__members__.items():
            self.current_operators.append(member.symbol)
        self.grouping_operators: tuple = ('(', ')')
        self.signs: tuple = ('+', '-')

    async def shunt_yard(self, flat_tokens: list):
        await self.flush_stacks()
        complete_tokens: list = await self.consolidate_tokens(flat_tokens)
        await self.process_input(complete_tokens)
        final_result = await self.evaluate_input()
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
                elif not previous_is_operator:
                    previous_is_operator = True
                else:
                    raise DuplicateOperator
            elif current_token in self.current_functions:
                if next_token and next_token in self.grouping_operators:
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
                    current_has_precedence = await ShuntOperator.compare_precedence(self.operator_stack[0],
                                                                                    complete_tokens[index],
                                                                                    ShuntComparison.GREATER_THAN)
                    last_equal_precedence = await ShuntOperator.compare_precedence(self.operator_stack[0],
                                                                                   complete_tokens[index],
                                                                                   ShuntComparison.EQUAL_TO)
                    last_left_associative = await ShuntOperator.compare_associativity(self.operator_stack[0],
                                                                                      ShuntAssociativity.LEFT)
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
                second_operand: int = output_stack.pop(0)
                first_operand: int = output_stack.pop(0)
                relevant_operator = await ShuntOperator.get_by_symbol(output)
                operation_result = await ShuntOperator.evaluate_operator(relevant_operator.value, first_operand,
                                                                         second_operand)
                output_stack.insert(0, operation_result)
            elif output in self.current_functions:
                first_operand: int = output_stack.pop(0)
                relevant_function = await ShuntFunction.get_by_name(output)
                operation_result = await ShuntFunction.evaluate_function(relevant_function.value, first_operand)
                output_stack.insert(0, operation_result)
            else:
                output_stack.insert(0, output)
        return output_stack[0]
