import json
import sys

class Environment:
    """
    Represents a scope where variables are stored. Each environment can optionally
    have a parent environment, allowing variable look-up in nested scopes.
    """
    def __init__(self, parent=None):
        # Dictionary to store variables in the current environment
        self.variables = {}
        # Reference to the parent environment (optional)
        self.parent = parent

    def set_variable(self, name, value):
        """
        Sets a variable in the current environment.
        :param name: The name of the variable to set
        :param value: The value to assign to the variable
        """
        self.variables[name] = value

    def get_variable(self, name):
        """
        Retrieves a variable's value from the current environment.
        If not found, it checks the parent environment (if exists).
        :param name: The name of the variable to retrieve
        :return: The value of the variable
        :raises NameError: If the variable is not found in any environment
        """
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise NameError(f"Variable '{name}' not found")

class Function:
    """
    Represents a user-defined function with parameters, a body, and its own environment.
    """
    def __init__(self, params, body, environment):
        # List of parameter names for the function
        self.params = params
        # List of expressions that form the body of the function
        self.body = body
        # Environment where the function was defined
        self.environment = environment

class Interpreter:
    """
    The interpreter executes a series of expressions in a given environment.
    It can evaluate expressions and supports operations such as setting variables,
    function definition, and arithmetic.
    """
    def __init__(self):
        # Global environment shared across all expressions
        self.global_env = Environment()

    def evaluate(self, expr, environment):
        """
        Evaluates an expression in the specified environment.
        :param expr: The expression to evaluate
        :param environment: The environment to use for variable look-up and storage
        :return: The result of the evaluated expression
        """
        if isinstance(expr, int):
            # Base case: if the expression is not a list, it's treated as a constant value
            return expr
        assert isinstance(expr, list)


        # First element is the operation (e.g., "add", "set", "call")
  
        operation = expr[1] if expr[1] in ["+", "-", "/", "*","XOR", "OR", "AND"] else expr[0]

        if operation == "seq":
            # Executes a sequence of expressions, returning the result of the last one
            assert len(expr[1:]) > 0
            result = None
            for element in expr[1:]:
                result = self.evaluate(element, environment)
            return result

        elif operation == "set":
            # Sets a variable to a value
            name = expr[1]
            value = self.evaluate(expr[2], environment)
            environment.set_variable(name, value)
            return value

        elif operation == "get":
            # Retrieves the value of a variable
            name = expr[1]
            return environment.get_variable(name)

        elif operation == "func":
            # Defines a function with parameters and body
            params = expr[1]
            body = expr[2:]
            return Function(params, body, environment)

        elif operation == "call":
            # Calls a function with arguments
            func_name = expr[1]
            func = environment.get_variable(func_name)
            args = [self.evaluate(arg, environment) for arg in expr[2:]] if len(expr) > 2 else []
            call_env = Environment(func.environment)
            for param, arg in zip(func.params, args):
                call_env.set_variable(param, arg)
            result = None
            for element in func.body:
                result = self.evaluate(element, call_env)
            return result

        elif operation == "print":
            # Prints a value to the console
            value = self.evaluate(expr[1], environment)
            print(value)
            return value

        elif operation == "add":
            # Adds two numbers
            a = self.evaluate(expr[1], environment)
            b = self.evaluate(expr[2], environment)
            return a + b

        elif operation == "abs":
            # Returns the absolute value of a number
            value = self.evaluate(expr[1], environment)
            return abs(value)

        elif operation == "+":

            # Adds two numbers (alternate syntax for "add")
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)

            return a + b

        elif operation == "-":
            # Subtracts two numbers
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)
            return a - b

        elif operation == "*":
            # Multiplies two numbers
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)
            return a * b

        elif operation == "/":
            # Divides two numbers
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)
            return a / b

        elif operation == "AND":
            # Logical AND operation
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)
            return expr[0]==1 and expr[2] == 1

        elif operation == "OR":
            # Logical OR operation
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)
            return expr[0]==1 or expr[2] == 1

        elif operation == "XOR":
            # Logical XOR operation
            a = self.evaluate(expr[0], environment)
            b = self.evaluate(expr[2], environment)
            return expr[0]==1 ^ expr[2] == 1

        else:
            # Error for unknown operation
            raise SyntaxError(f"Unknown operation: {operation}")
    


def main():
    """
    Entry point of the program that reads a program file from the command line
    and executes it using the interpreter.
    """
    # Check if a file name argument was provided
    if len(sys.argv) != 2:
        print("Usage: python lgl_interpreter.py <filename>")
        return

    # Get the file name from the command line argument
    filename = sys.argv[1]

    try:
        # Open the specified file and load the program
        with open(filename, "r") as f:
            example_program = json.load(f)

        # Initialize interpreter and evaluate the loaded program
        interpreter = Interpreter()
        interpreter.evaluate(example_program, interpreter.global_env)

    except FileNotFoundError:
        print(f"File not found: {filename}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {filename}")


if __name__ == "__main__":
    main()
