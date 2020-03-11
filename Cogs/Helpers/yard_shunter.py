from Cogs.Helpers.Enumerators.shunters import ShuntAssociativity, ShuntFunction, ShuntOperator, ShuntComparison
import re


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

    async def shunt_yard(self, ctx, flat_tokens: list):
        await self.flush_stacks()
        complete_tokens: list = await self.consolidate_tokens(ctx, flat_tokens)
        await self.process_input(ctx, complete_tokens)
        final_result = await self.evaluate_input(ctx)
        return final_result

    async def flush_stacks(self):
        self.operator_stack.clear()
        self.output_queue.clear()

    # TODO: simplify this / improve readability? feels clunky.
    async def consolidate_tokens(self, ctx, flattened_tokens: list):
        operator_bool: bool = False
        index: int = 0
        while index < len(flattened_tokens):
            if (operator_bool or index == 0) and flattened_tokens[index] in self.signs:
                if (index + 1) < len(flattened_tokens) and flattened_tokens[index + 1].isdigit():
                    flattened_tokens[index] = int(flattened_tokens[index] + flattened_tokens[index + 1])
                    del flattened_tokens[index + 1]
                    operator_bool = False
                elif operator_bool:
                    # TODO: actually raise an error?
                    await ctx.send("Error: Invalid sign duplication in roll modifier. Please try again!")
                elif index == 0 and (index + 1) < len(flattened_tokens) and \
                        not flattened_tokens[index + 1].isdecimal():
                    if flattened_tokens[index] == '+':
                        flattened_tokens[index] = 1
                    else:
                        flattened_tokens[index] = -1
                    flattened_tokens.insert(1, '*')
            elif flattened_tokens[index] in self.current_operators:
                operator_bool = True
            elif flattened_tokens[index].isdigit():
                flattened_tokens[index] = int(flattened_tokens[index])
                operator_bool = False
            index += 1
        return flattened_tokens

    async def process_input(self, ctx, complete_tokens: list):
        index: int = 0
        while index < len(complete_tokens):
            if isinstance(complete_tokens[index], int):
                self.output_queue.append(int(complete_tokens[index]))
            elif complete_tokens[index] in self.current_functions:
                self.operator_stack.insert(0, complete_tokens[index])
            elif complete_tokens[index] in self.current_operators:
                while self.operator_stack and self.operator_stack[0] != '(' and \
                        (self.operator_stack[0] in self.current_functions or
                         await ShuntOperator.compare_precedence(ctx, self.operator_stack[0], complete_tokens[index],
                                                                ShuntComparison.GREATER_THAN) or
                         (await ShuntOperator.compare_precedence(ctx, self.operator_stack[0], complete_tokens[index],
                                                                 ShuntComparison.EQUAL_TO) and
                          await ShuntOperator.compare_associativity(ctx, self.operator_stack[0],
                                                                    ShuntAssociativity.LEFT.direction))):
                    self.output_queue.append(self.operator_stack.pop(0))
                self.operator_stack.insert(0, complete_tokens[index])
            elif complete_tokens[index] == '(':
                self.operator_stack.insert(0, complete_tokens[index])
            elif complete_tokens[index] == ')':
                while self.operator_stack and self.operator_stack[0] != '(':
                    self.output_queue.append(self.operator_stack.pop(0))
                if self.operator_stack[0] == '(':
                    self.operator_stack.pop(0)
                else:
                    # TODO: actually raise error?
                    await ctx.send("Error: mismatched parentheses in roll modifier. Please try again!")
            index += 1
        else:
            while self.operator_stack:
                if self.operator_stack[0] in ['(', ')']:
                    # TODO: actually raise error?
                    await ctx.send("Error: mismatched parentheses in roll modifier. Please try again!")
                else:
                    self.output_queue.append(self.operator_stack.pop(0))

    async def evaluate_input(self, ctx):
        output_stack: list = []
        for output in self.output_queue:
            if output in self.current_operators:
                second_operand: int = output_stack.pop(0)
                first_operand: int = output_stack.pop(0)
                relevant_operator = await ShuntOperator.get_by_symbol(ctx, output)
                operation_result = await ShuntOperator.function_evaluator(relevant_operator.value,
                                                                          first_operand, second_operand)
                output_stack.insert(0, operation_result)
            elif output in self.current_functions:
                first_operand: int = output_stack.pop(0)
                relevant_function = await ShuntFunction.get_by_name(ctx, output)
                operation_result = await ShuntFunction.function_evaluator(relevant_function.value,
                                                                          first_operand)
                output_stack.insert(0, operation_result)
            else:
                output_stack.insert(0, output)
        return output_stack[0]
