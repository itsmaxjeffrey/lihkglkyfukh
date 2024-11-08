import json
from typing import Any, Dict, List, Union

class Environment:
    def __init__(self, parent=None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent

    def set(self, name: str, value: Any) -> None:
        self.vars[name] = value

    def get(self, name: str) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' not found")

class Function:
    def __init__(self, params: List[str], body: List[Any], env: Environment):
        self.params = params
        self.body = body
        self.env = env  # Capture the lexical environment

class Interpreter:
    def __init__(self):
        self.global_env = Environment()

    def eval(self, expr: Union[List, str], env: Environment) -> Any:
        if not isinstance(expr, list):
            # If it's not a list, it might be a literal value or variable
            if isinstance(expr, str):
                return env.get(expr)
            return expr

        op = expr[0]

        if op == "seq":
            result = None
            for sub_expr in expr[1:]:
                result = self.eval(sub_expr, env)
            return result

        elif op == "set":
            name = expr[1]
            value = self.eval(expr[2], env)
            env.set(name, value)
            return value

        elif op == "get":
            name = expr[1]
            return env.get(name)

        elif op == "func":
            # Capture lexical environment and return a Function object
            params = expr[1]
            body = expr[2:]
            return Function(params, body, env)

        elif op == "call":
            # Evaluate the function reference (it could be a variable holding a function)
            func = self.eval(expr[1], env)
            if not isinstance(func, Function):
                raise TypeError(f"{func} is not a callable function")

            # Evaluate arguments
            args = [self.eval(arg, env) for arg in expr[2:]] if len(expr) > 2 else []
            
            # Create a new environment with the function's lexical scope
            call_env = Environment(func.env)
            
            # Bind parameters to arguments
            for param, arg in zip(func.params, args):
                call_env.set(param, arg)
            
            # Execute all expressions in function body
            result = None
            for sub_expr in func.body:
                result = self.eval(sub_expr, call_env)
            return result

        elif op == "print":
            value = self.eval(expr[1], env)
            print(value)
            return value

        else:
            raise SyntaxError(f"Unknown operation: {op}")

    def run_file(self, filename: str) -> Any:
        with open(filename, 'r') as f:
            program = json.load(f)
            return self.eval(program, self.global_env)

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
