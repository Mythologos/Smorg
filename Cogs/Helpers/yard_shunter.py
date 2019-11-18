from Cogs.Helpers.Enumerators.shunt_aids import ShuntAssociativity, ShuntFunction, ShuntOperator, ShuntComparison


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

    def shunt_yard(self, user_input: str):
        self.process_input(user_input)
        final_result = self.evaluate_input()
        self.flush_stacks()
        return final_result

    def flush_stacks(self):
        self.operator_stack.clear()
        self.output_queue.clear()

    def process_input(self, user_input: str):
        while user_input:
            full_number: str = ''
            while user_input and user_input[0].isalnum():
                full_number += user_input[0]
                user_input = user_input[1:]
            if full_number:
                self.output_queue.append(int(full_number))
            elif not user_input:
                continue
            else:
                if user_input[0] in self.current_functions:
                    self.operator_stack.insert(0, user_input[0])
                elif user_input[0] in self.current_operators:
                    while self.operator_stack and self.operator_stack[0] != '(' and \
                            (self.operator_stack[0] in self.current_functions or
                             ShuntOperator.compare_precedence(self.operator_stack[0], user_input[0],
                                                              ShuntComparison.GREATER_THAN) or
                             (ShuntOperator.compare_precedence(self.operator_stack[0], user_input[0],
                                                               ShuntComparison.EQUAL_TO) and
                              ShuntOperator.compare_associativity(self.operator_stack[0],
                                                                  ShuntAssociativity.LEFT.associativity))):
                        self.output_queue.append(self.operator_stack.pop(0))
                    self.operator_stack.insert(0, user_input[0])
                elif user_input[0] == '(':
                    self.operator_stack.insert(0, user_input[0])
                elif user_input[0] == ')':
                    while self.operator_stack and self.operator_stack[0] != '(':
                        self.output_queue.append(self.operator_stack.pop(0))
                    if self.operator_stack[0] == '(':
                        self.operator_stack.pop(0)
                    else:
                        ...
                        print("Error3!")
                        # throw error, mismatched parentheses
                user_input = user_input[1:]
        else:
            while self.operator_stack:
                if self.operator_stack[0] in ['(', ')']:
                    ...
                    print("Error2!")
                    # throw error, mismatched parentheses
                else:
                    self.output_queue.append(self.operator_stack.pop(0))

    def evaluate_input(self):
        output_stack: list = []
        for output in self.output_queue:
            if output in self.current_operators:
                second_operand: int = output_stack.pop(0)
                first_operand: int = output_stack.pop(0)
                operation_result = ShuntOperator.function_evaluator(ShuntOperator.get_by_symbol(output).value,
                                                                    first_operand, second_operand)
                output_stack.insert(0, operation_result)
            elif output in self.current_functions:
                first_operand: int = output_stack.pop(0)
                operation_result = ShuntFunction.function_evaluator(ShuntOperator.get_by_symbol(output).value,
                                                                    first_operand)
                output_stack.insert(0, operation_result)
            else:
                output_stack.insert(0, output)
        return output_stack[0]


# Tests:
# my_yard_shunter = YardShunter()
# my_first_result = my_yard_shunter.shunt_yard('3+4*2')
# my_result = my_yard_shunter.shunt_yard('((15/(7-(1+1)))*3)-(2+(1+1))')
