import json
from typing import Any, Dict, List, Union

# Environment class to hold variables and their values
class Environment:
    def __init__(self, parent=None):
        self.vars = {}  # Dictionary to store variables
        self.parent = parent  # Link to parent environment

    # Set a variable in this environment
    def set(self, name, value):
        self.vars[name] = value

    # Get a variable's value; check parent if it's not here
    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        # Raise error if not found in any environment
        raise NameError(f"Variable '{name}' not found")

# Function class to represent a function with parameters and body
class Function:
    def __init__(self, params, body, env):
        self.params = params  # Parameters the function takes
        self.body = body  # List of expressions in the function body
        self.env = env  # Environment where function was defined

# Interpreter to evaluate expressions
class Interpreter:
    def __init__(self):
        self.global_env = Environment()  # Global environment for program

    # Evaluates an expression based on the type of operation
    def eval(self, expr, env):
        # If it's not a list, treat it as a literal or variable
        if not isinstance(expr, list):
            if isinstance(expr, str):
                return env.get(expr)  # Look up variable
            return expr  # Just return the literal (like a number)

        op = expr[0]  # First item is the operation type

        if op == "seq":
            # Sequence of expressions; run each in order
            result = None
            for sub_expr in expr[1:]:
                result = self.eval(sub_expr, env)  # Update result
            return result  # Return the last result

        elif op == "set":
            # Set a variable in the current environment
            name = expr[1]
            value = self.eval(expr[2], env)
            env.set(name, value)
            return value

        elif op == "get":
            # Get a variable's value
            name = expr[1]
            return env.get(name)

        elif op == "func":
            # Define a function; store its params and body
            params = expr[1]
            body = expr[2:]
            return Function(params, body, env)

        elif op == "call":
            # Call a function with arguments
            func = self.eval(expr[1], env)  # Find the function
            if not isinstance(func, Function):
                raise TypeError(f"{func} is not callable")

            # Evaluate arguments
            args = [self.eval(arg, env) for arg in expr[2:]]
            
            # Create a new environment for the function call
            call_env = Environment(func.env)
            
            # Bind function parameters to the arguments
            for param, arg in zip(func.params, args):
                call_env.set(param, arg)
            
            # Run the function body
            result = None
            for sub_expr in func.body:
                result = self.eval(sub_expr, call_env)
            return result

        elif op == "print":
            # Print an expression's value
            value = self.eval(expr[1], env)
            print(value)
            return value

        else:
            # Raise an error if operation is unknown
            raise SyntaxError(f"Unknown operation: {op}")

    # Load and run a program from a JSON file
    def run_file(self, filename):
        with open(filename, 'r') as f:
            program = json.load(f)
            return self.eval(program, self.global_env)

# Main program
def main():
    example_program = [
        "seq",
        ["set", "x", 100],
        ["set", "outer", ["func", ["y"], 
            ["set", "z", ["func", ["a"], 
                ["print", ["get", "x"]],
                ["print", ["get", "y"]],
                ["print", ["get", "a"]]
            ]],
            ["call", "z", ["get", "y"]]
        ]],
        ["call", "outer", [200]]
    ]

    interpreter = Interpreter()
    result = interpreter.eval(example_program, interpreter.global_env)

if __name__ == "__main__":
    main()
