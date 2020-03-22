from Cogs.Helpers.Enumerators.shunters import ShuntAssociativity, ShuntFunction, ShuntOperator, ShuntComparison


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

    # Cases:
    # Negative at beginning of roll, e.g.:
    # -1+5 = -(1 * 1) + 5; -5d3 = -(5d3);
    # Negative in middle of roll, e.g.:
    # 5+-3 = 5 + (-1 * 3); 3d6+-floor(5/2) = 3d6 + (-1 * floor(5/2))
    async def consolidate_tokens(self, ctx, flattened_tokens: list):
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
                    raise NotImplementedError
                    # raise error, multiple operators in a row
            elif current_token in self.current_functions:
                if next_token and next_token in self.grouping_operators:
                    index += 1
                else:
                    raise NotImplementedError
                    # raise error, multiple operators in a row
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
                    # TODO: actually raise relevant error?
                    raise NotImplementedError
                    # await ctx.send("Error: mismatched parentheses in roll modifier. Please try again!")
            index += 1
        else:
            while self.operator_stack:
                if self.operator_stack[0] in self.grouping_operators:
                    # TODO: actually raise relevant error?
                    raise NotImplementedError
                    # await ctx.send("Error: mismatched parentheses in roll modifier. Please try again!")
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
