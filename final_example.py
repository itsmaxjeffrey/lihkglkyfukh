import sys
import json
import csv
from datetime import datetime
from uuid import uuid4


# trace part
# ------- trace event logger -------------
def log_event(id, timestamp, function_name, event):
    with open(sys.argv[3], mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [id, timestamp, function_name, event]
        )  # write the row to the csv file


# ------- trace function decorator -------------


def trace_function():
    """trace_function is a decorator that logs the start and stop of a function call to a log file

    Args:
        log_file (_type_): calls the log_event function to log call_id, start_time, function_name, event
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            function_name_holder = args[1][1]
            if function_name_holder != []:
                call_id = uuid4().int % 1000000
                start_time = datetime.now()
                log_event(call_id, start_time, function_name_holder[-1], "start")
                result = func(*args, **kwargs)
                end_time = datetime.now()
                log_event(call_id, end_time, function_name_holder[-1], "stop")
                return result
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


# helper function for the parse_infix that follows
def precedence(op):
    """Returns the precedence of an operator. This is used in our parse_infix func to maintain
    precedence of operators

    Parameters
    ----------
    op : str
        "AND", "OR", "XOR", "+", "-", "*", "/"

    Returns
    -------
    int
        The precedence of the operator

    """

    if op in ["AND", "OR", "XOR"]:
        return 1
    if op in ["+", "-"]:
        return 2
    if op in ["*", "/"]:
        return 3


def parse_infix(expr, scope_trace):
    """Using the shunting-yard algorithm, this function parses an infix expression into a list of arguments
    in Reverse Polish Notation (RPN) i.e. postfix notation
    Example: [2 "+", 3] -> [2, 3, "+"]
    This order explained in evaluate_rpn function.
    This function also evaluates nested expressions using the "do" function


    Parameters
    ----------
    expr : list
        The infix expression to parse, including perhaps nested expressions

    Returns
    -------
    list
        The expression in RPN (without nested lists), allowing precedence of
        operators defined in our precedence function.

    """
    # infix expr has to be at least a simple binary operation, [1 + 2] should be invalid
    assert len(expr) >= 3
    output_queue = []
    operator_stack = []
    for arg in expr:
        if isinstance(arg, int):  # numbers go straight to the output queue
            output_queue.append(arg)
        elif isinstance(arg, list):  # nested lists must first be evaluated
            value = do(arg, scope_trace)
            output_queue.append(value)  # then the value gets added to the output queue
        ## if arg not number or list, must be an operator. check if op stack not empty, check precedence
        ## if an equal or higher precedence operator already in stack, this gets popped to the queue
        elif operator_stack and precedence(arg) <= precedence(operator_stack[-1]):
            output_queue.append(operator_stack.pop())
            # before the operator of the current iteration gets added to the stack
            operator_stack.append(arg)
        else:  # otherwise the current operator just gets added onto the operator stack directly
            operator_stack.append(arg)
    # pop all remaining operators from the stack to the output queue
    while operator_stack:
        output_queue.append(operator_stack.pop())
    return output_queue


def evaluate_rpn(expr):
    """The main function that computes the result of our infix expression. It gets the expression already
    parsed into RPN (postfix) order. Starting with an empty stack, we go thru this rpn list term for term
    popping 2 numbers and an operator and pushing this result back onto the stack
    This way we go thru the whole expression and end up with the final value.

    Parameters
    ----------
    expr : list
        The expression in RPN

    Returns
    -------
    int
        The final result of the expression
    """

    evaluation_stack = []
    for arg in expr:
        if isinstance(arg, int):
            evaluation_stack.append(arg)
        else:
            # since the RPN expression was created in lifo order, the 2nd operand gets popped before the 1st
            # this ensures we keep left associativity (important for minus and divide where order matters)
            operand2 = evaluation_stack.pop()
            operand1 = evaluation_stack.pop()
            if arg == "+":
                result = operand1 + operand2
                evaluation_stack.append(result)  # push the result back to the stack
            elif arg == "-":
                result = operand1 - operand2
                evaluation_stack.append(result)
            elif arg == "*":
                result = operand1 * operand2
                evaluation_stack.append(result)
            elif arg == "/":
                if operand2 == 0:
                    raise ZeroDivisionError("Division by zero is undefined")
                result = operand1 / operand2
                evaluation_stack.append(result)
            elif arg == "AND":
                # python usually returns 2nd value if both are True.. so we need to convert to 1 or 0
                result = int(bool(operand1) and bool(operand2))
                evaluation_stack.append(result)
            elif arg == "OR":
                # similar to AND, but returns 1 if any of the values is True
                result = int(bool(operand1) or bool(operand2))
                evaluation_stack.append(result)
            elif arg == "XOR":
                # again here, we want 1 for T and 0 for F, and only true if not equal
                # we decide to make it only check for equality ie 1 XOR 2 would be true because they're not equal
                result = int(bool(operand1 != operand2))
                evaluation_stack.append(result)
    assert len(evaluation_stack) == 1
    return evaluation_stack[0]


# ------- lexical scope changes done from here (not yet for infix operation) -------------


### START - do_ FUNCTIONS ###
## start - do_ for functionality reasons
@trace_function()
def do_add(args, scope_trace):
    """Handles the 'addieren' operation; e.g., ["addieren",1,2]

    Parameters
    ----------
    envs_stack : list
        The stack with the environments
    args : list
        The list of the two values to add
        (they can be other operations)

    Returns
    -------
    int
        the sum of the two values
    """

    assert len(args) == 2
    left = do(args[0], scope_trace)
    right = do(args[1], scope_trace)

    return left + right


@trace_function()
def do_power(args, scope_trace):

    assert len(args) == 2

    left = do(args[0], scope_trace)
    right = do(args[1], scope_trace)

    return left**right


## end - do_ for functionality reasons
## start - do_ for structural purposes
def do_seq(args, scope_trace):
    """Handles the 'seq' operation

    Example:
    ["seq",
        ["set", "alpha", 1],
        ["get", "alpha"]
    ]

    Parameters
    ----------
    envs_stack : list
        The stack with the environments
    args : list
        The list of operations to execute

    Returns
    -------
    int
        the return value of the last operation
        in the list of args
    """

    assert len(args) > 0
    result = None
    for expr in args:
        result = do(expr, scope_trace)
    return result


@trace_function()
def do_set(args, scope_trace):
    """Handles the 'set' operation; e.g., ["set", "alpha", 1]

    Parameters
    ----------
    envs_stack : list
        The stack with the environments
        where to store/update the variable
    args : list
        args[0] : name of variable
        args[1] : content of variable

    Returns
    -------
    int
        the value associated to the var
    """

    assert len(args) == 2
    assert isinstance(args[0], str)
    var_name = args[0]

    is_func = check_for_func(args[1])
    value = do(args[1], scope_trace)

    # making sure that variable is set in the right scope
    # for more information check set_in_scope_dict and check_for_func
    if is_func:
        set_in_scope_dict(var_name, value, scope_trace[0], True)
    else:
        set_in_scope_dict(var_name, value, scope_trace[1])
    return value


@trace_function()
def do_get(args, scope_trace):
    """Handles the 'get' operation; e.g., ["get", "alpha"]

    Parameters
    ----------
    envs_stack : list
        The stack with the environments
        from which to retrieve the variable
    args : str
        The name of the variable

    Returns
    -------
    object
        the content of the variable
    """

    assert len(args) == 1
    assert isinstance(args[0], str)
    # TODO: Comment functionality regarding lexical scoping
    value = get_from_scope_dict(args[0], scope_trace[1])
    return value


@trace_function()
def do_function(args, scope_trace):
    """Handles the 'func' operation; ["func", "n", ["get","n"]]

    This function does not do much: it only
    prepares the data structure to store in
    memory, which can then be called later

    Parameters
    ----------
    envs_stack : list
        The stack with the environments
        (only here for consistency)
    args : list
        args[0] : parameters of the function
        args[1] : body of the function

    Returns
    -------
    list
        the list with parameters and body
    """

    assert len(args) == 2
    parameters = args[0]
    body = args[1]
    return ["function", parameters, body]


@trace_function()
def do_call(args, scope_trace):
    """Handles the 'call' operation; e.g., ["call","add_two",3,2]

    where "add_two" is the name of a function
    previously defined, and the rest are the
    arguments to pass to the function

    Parameters
    ----------
    envs_stack : list
        The stack with the environments,
        to which it pushes the specific env
        for the function when called and
        pop it afterwards
    args : list
        args[0] : name of function to call
        args[1] : arguments to pass to func

    Returns
    -------
    object
        the return value of the body execution
    """

    # setting up the call
    assert len(args) >= 1
    assert isinstance(args[0], str)
    func_name = args[0]  # "add_two"
    arguments = [do(a, scope_trace) for a in args[1:]]  # [3, 2]
    # find the function
    func = get_from_scope_dict(func_name, scope_trace[1])
    assert (
        isinstance(func, list) and func[0] == "function"
    ), f"{func_name} is not a function!"
    params = func[1]  # ["num1","num2"]
    body = func[2]  # ["addieren","num1","num2"]
    assert len(arguments) == len(
        params
    ), f"{func_name} receives a different number of parameters"

    # making sure the assignment of arguments to parameters happens in the current exicuting function
    for param, arg in zip(params, arguments):
        set_in_scope_dict(param, arg, scope_trace[1])

    # keeping track of function execution for lexical scoping (e.g. that the passed variables are set in the right scope)
    scope_trace[1].append(func_name)
    result = do(body, scope_trace)
    scope_trace[1].append(func_name)

    return result


## start - do_ for structural purposes
### END - do_ FUNCTIONS ###

### START - HELPERS FOR LEXICAL SCOPING

# will house keys (str) and associated tuples (value of any type, {})
# the dict at position 1 represents the scope of that value/thing
# it is empty for  e.g. values of type int but will eventually have content when the value is a function (definition)
SCOPES = {}


def set_in_scope_dict(name, value, scope_trace_path: list, is_func=False):
    """Adds a variable and its value to the scope dictionary.

    To associate function definition with its name use
        scope_trace[0] as scope_trace_path,
        True as is_func

    To associate value with its variable name (also e.g. in function scope) use
        scope_trace[1] as scope_trace_path,
        False as is_func

    Parameters
    ----------
    name : str
        name of the variable to set
    value : object
        value to associate to the variable
    scope_trace_path : list
        the names (keys) that define the scope layers/"path" in the scope dictionary
        where the variable should be set
    is_func : bool
        set True if the associated value is a function definition
        defaults to False

    Returns
    -------
    None
        nothing is returned, could have returned the set value
    """

    assert isinstance(name, str)

    # navigating the scope dict to the scope level where the variable should be set
    dest = SCOPES
    for level in scope_trace_path:
        try:
            dest = dest[level][1]
        except KeyError:
            break
        except Exception as e:
            assert False, f"An unexpected error {e} occured when trying to set {name}"

    # associating value (and its own scope level dict!) with the variable name (key)
    dest[name] = (value, {})

    # keeping track of DEFINITION scope for nested function definition
    if is_func:
        scope_trace_path.append[name]


def get_from_scope_dict(name, execution_scope_trace: list):
    """
    Searches and returns value associated with variable name based on current scope.

    Parameters
    ----------
    name : str
        name of the variable to set

    execution_scope_trace : list
        the names (keys) that define the scope layers/"path" in the scope dictionary
        where the variable should be set

    Returns
    -------
    any
        the value associated with name
    """
    # TODO (AP): Check retrieval when call trace and lexical definition trace do not match -> probably issue in logic!

    value = None
    scope = SCOPES

    # following the search trace and updating the with name associated value according to prescedence
    if name in scope.keys():
        value = scope[name][0]
    for level in execution_scope_trace:
        try:
            scope = scope[level][1]
        except KeyError:
            break
        if name in scope.keys():
            value = scope[name][0]
    return value


# used in do_set to use the right configuration of set_in_scope_dict
def check_for_func(arg):
    if not isinstance(arg, list):
        return False
    if not arg[1] == "function":
        return False
    return True


# TODO (AP): clean up after to-do in get_from_scope_dict is done
# def get_scope_trace(search_term: str, level=SCOPES):
#     trace = []
#     if search_term in level.keys():
#         return level[key], trace
#     for key, value in level.items():
#         return get_from_scope_dict(search_term, value[1])
#     assert False, f"Variable {search_term}, was not defined"

### END- HELPERS FOR LEXICAL SCOPING

### START - MAIN FUNCTIONALITIES FOR EXECUTION

# dynamically find and name all operations we support in our language
OPS = {
    name.replace("do_", ""): func
    for (name, func) in globals().items()
    if name.startswith("do_")
}


def do(expr, scope_trace):
    """Executes the given expression

    Our minimal operation is an integer value; everything else is
    then computed to a value.

    Parameters
    ----------
    expr : object
        The expression to compute
    scope_trace :

    Returns
    -------
    object
        value of the computed operation
    """
    # numbers just get returned
    if isinstance(expr, int):
        return expr

    # if not a number, we require it to be a list
    if not isinstance(expr, list):
        raise ValueError(f"Unknown expression: {expr}")

    # if the 1st element of this list is a str, it is an operation
    if isinstance(expr[0], str):
        if expr[0] not in OPS:  # make sure we have it in our OPS dict
            raise ValueError(f"Unknown operation: {expr[0]}")
        else:
            operation = OPS[expr[0]]
            return operation(expr[1:], scope_trace)
    # if the first element is not a string, it must be an operand of an infix expression
    else:
        tokens = parse_infix(
            expr, scope_trace
        )  #  parse_infix now also takes scope_trace
        result = evaluate_rpn(tokens)
        return result


def main():
    """Executes the interpreter on the given code file.

    The function also creates the global environment and the stack of
    enviroments, which will be then passed around. It prints the result
    of the computation.

    """
    program = ""
    if len(sys.argv) > 2 and sys.argv[2] == "--trace":
        # TODO: Introduce funcationality that allows user to specify the trace file name.
        # So that the decorators can use it
        assert (
            len(sys.argv) == 4
        ), "usage: python interpreter.py example_trace.gsc --trace trace.log"
    else:
        assert len(sys.argv) == 2, "usage: python interpreter.py code.tll"
    with open(sys.argv[1], "r") as source:
        program = json.load(source)
    scope_trace = (
        [],
        [],
    )  # scope_trace[0] for definition, scope_trace[1] for current execution scope
    result = do(program, scope_trace)
    print(result)


### END - MAIN FUNCTIONALITIES FOR EXECUTION

if __name__ == "__main__":
    main()
