import json
from typing import Any, Dict, List, Union

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def set(self, name, value):
        self.vars[name] = value

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' not found")

class Function:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

class Interpreter:
    def __init__(self):
        self.global_env = Environment()

    def eval(self, expr, env):
        if not isinstance(expr, list):
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
            params = expr[1]
            body = expr[2:]
            return Function(params, body, env)

        elif op == "call":
            func = self.eval(expr[1], env)
            if not isinstance(func, Function):
                raise TypeError(f"{func} is not callable")

            args = [self.eval(arg, env) for arg in expr[2:]]
            call_env = Environment(func.env)
            
            for param, arg in zip(func.params, args):
                call_env.set(param, arg)
            
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

    def run_file(self, filename):
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
