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
            # If it's not a list, it might be a literal value
            return expr

        op = expr[0]

        if op == "seq":
            result = None
            for e in expr[1:]:
                result = self.eval(e, env)
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
            params = expr[1]
            body = expr[2:]
            return Function(params, body, env)

        elif op == "call":
            func_name = expr[1]
            func = env.get(func_name)
            args = [self.eval(arg, env) for arg in expr[2:]] if len(expr) > 2 else []
            
            # Create new environment with captured lexical scope
            call_env = Environment(func.env)
            
            # Bind parameters to arguments
            for param, arg in zip(func.params, args):
                call_env.set(param, arg)
            
            # Execute all expressions in function body
            result = None
            for e in func.body:
                result = self.eval(e, call_env)
            return result

        elif op == "print":
            value = self.eval(expr[1], env)
            print(value)
            return value

        elif op == "add":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return a + b

        elif op == "abs":
            value = self.eval(expr[1], env)
            return abs(value)

        elif op == "+":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return a + b

        elif op == "-":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return a - b

        elif op == "*":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return a * b

        elif op == "/":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return a / b

        elif op == "and":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return bool(a) and bool(b)

        elif op == "or":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return bool(a) or bool(b)

        elif op == "xor":
            a = self.eval(expr[1], env)
            b = self.eval(expr[2], env)
            return bool(a) ^ bool(b)

        else:
            raise SyntaxError(f"Unknown operation: {op}")

    def run_file(self, filename: str) -> Any:
        with open(filename, 'r') as f:
            program = json.load(f)
            return self.eval(program, self.global_env)

def main():
    # Example program
    example_program = [
        "seq",
        ["set", "x", 100],
        ["set", "two", ["func", [], ["set", "x", 42], ["call", "one", ["get", "x"]]]],
        ["set", "one", ["func", ["y"], ["print", ["get", "y"]]]],
        ["call", "two"],
        ["set", "a", ["add", 3, 4]],
        ["set", "b", ["abs", -5]],
        ["set", "c", ["+", 5, 10]],
        ["set", "d", ["-", 20, 7]],
        ["set", "e", ["*", 3, 4]],
        ["set", "f", ["/", 100, 5]],
        ["set", "g", ["and", 1, 1]],
        ["set", "h", ["or", 1, 0]],
        ["set", "i", ["xor", 1, 1]]
    ]

    interpreter = Interpreter()
    
    # You can either run the example program directly:
    result = interpreter.eval(example_program, interpreter.global_env)
    
    # Or load from a JSON file:
    # result = interpreter.run_file("program.json")

if __name__ == "__main__":
    main()
