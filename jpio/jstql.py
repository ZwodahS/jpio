
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Check out https://github.com/ZwodahS/jpio for the latest version of the software.

import json
import copy
from functools import reduce

################################################### Common Stuffs #####################################################
def recursive_copy(data):
    if isinstance(data, dict):
        return { k : recursive_copy(v) for k, v in data.items() }
    elif isinstance(data, list):
        return [ recursive_copy(v) for v in data ]
    elif isinstance(data, tuple):
        return tuple([ recursive_copy(v) for v in data.items() ])
    elif data is None or type(data) in [ int, float, complex, str, bool ]:
        return data
    return data.copy()
#################### Exception ####################
class JSTQLException(Exception):
    def __init__(self, message=None):
        self.message = message or "unknown error"

    def __str__(self):
        return self.message


class JSTQLParserException(JSTQLException):
    def __init__(self, query_string, index, message):
        super().__init__(message)
        self.query_string = query_string
        self.index = index

    def __str__(self):
        line = []
        line.append(" query : {0}".format(self.query_string))
        line.append("         {0}".format("".join(([" "] * self.index) + ["^"])))
        line.append(" error : {0}".format(self.message))
        return "\n".join(line)


class JSTQLRuntimeException(JSTQLException):
    def __init__(self, current_state, message):
        super().__init__(message)
        self.current_state = current_state

    def __str__(self):
        line = []
        # disabled as this might sometime print the whole file
        # line.append(" current state : {0}".format(self.current_state))
        line.append(" error : {0}".format(self.message))
        return "\n".join(line)


class ModifierNotAllowed(JSTQLException):

    def __init__(self):
        self.message = "modifier not allowed"

#################### Node ####################

class Command(object):

    def __str__(self):
        return "({0})".format(type(self).__name__)


class Selector(Command):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "({0}:{1})".format(type(self).__name__, self.value)


class Iterator(Command):

    def __init__(self, value): # value can be tuple or a string "*"
        self.value = value


class Statement(Command):

    def __init__(self, commands=None):
        self.commands = commands or []

    def __str__(self):
        return ",".join([c.__str__() for c in self.commands])


class PipedStatement(Command):

    def __init__(self, statements=None):
        self.statements = statements or []


class Assignment(Command):

    def __init__(self, selector, value):
        self.selector = selector
        self.value = value


class FunctionChain(Command):

    def __init__(self, functions=None):
        self.functions = functions or []


class Function(Command):

    def __init__(self, name, args):
        self.name = name
        self.args = args


class ListConstruction(Command):

    def __init__(self, statements):
        self.statements = statements



SPECIAL_CHARS = (",", "[", "]", "#", ".", "(", ")", "=", ":", "|")

#################################################### Parser Stuffs ####################################################

class ParserContext(object):
    """
    A Parser context holds the current index that we are processing and the query_string.
    """

    def __init__(self, index, query_string):
        self.index = index
        self.query_string = query_string

    def next(self, amount=1):
        v = self.peek(amount)
        self.pop(amount)
        return v

    def pop(self, amount=1):
        self.index += amount
        if self.index > len(self.query_string):
            self.index = len(self.query_string)

    def peek(self, length):
        if self.index >= len(self.query_string) or self.index < 0:
            return None
        return self.query_string[self.index:self.index+length]

    def match(self, matchlist):
        if isinstance(matchlist, list):
            return any(map(lambda m : self.peek(len(m)) == m, matchlist))
        elif isinstance(matchlist, str):
            return self.peek(len(matchlist)) == matchlist
        return False

    def has_more(self):
        return self.index < len(self.query_string) and self.index >= 0


def _expects(context, values):
    if not isinstance(values, list):
        values = [values]
    expected = ' or '.join(values)

    if not context.has_more():
        raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected end of query, expects {0}".format(expected))
    if not context.match(values):
        max_length = reduce(lambda x, y : x if x > y else y, (len(v) for v in values), 0)
        raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected character '{0}', expects '{1}'".format(context.peek(max_length), expected))


def parse(query_string):
    context = ParserContext(index=0, query_string=query_string)
    return _parse_statement(context)


def _parse_statement(context, end=None):
    end = end or []
    statements = []
    commands = []
    last_command=False
    while context.has_more():
        if context.match(end):
            break
        if last_command and context.has_more() and not context.match("|"):
            raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Statement of type {0} must be the last statement".format(type(commands[-1]).__name__))
        if context.match("["):
            if len(commands) > 0:
                raise JSTQLParserException(query_string=context.query_string, index=context.index, message="List construction cannot happen in the middle of query")
            list_construction = _parse_list_construction(context)
            return Statement(commands=[list_construction])
        if context.match("("):
            context.pop() # pop (
            statement = _parse_statement(context, end=end+[")"])
            _expects(context, ")")
            context.pop() # pop )
            return statement
        elif context.match("|"):
            statement, commands = Statement(commands=commands), []
            statements.append(statement)
            last_command=False
            context.pop() # pop |
        elif context.match(".["):
            commands.append(_parse_iterator(context))
        elif context.match("."):
            commands.append(_parse_selector(context))
        elif context.match("="):
            if len(commands) == 0:
                raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error: Cannot assign to root")
            assignment_target, commands = commands[-1], commands[0:-1]
            commands.append(_parse_assignment(context, assignment_target,end=end))
            last_command=True
        elif context.match("#"):
            commands.append(_parse_functionchain(context))
            last_command=True
        else:
            raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Errror : Unexpected character '{0}'".format(context.peek(1)))

    statement, commands = Statement(commands=commands), []
    statements.append(statement)
    if len(statements) == 1:
        return statements[0]
    else:
        return PipedStatement(statements=statements)


def _parse_functionchain(context):

    chain = []
    while context.match("#"):
        function = _parse_function(context)
        chain.append(function)
    return FunctionChain(chain)


def _parse_function(context):
    _expects(context, "#")
    context.pop()
    end = list(SPECIAL_CHARS)
    end.remove('.')
    funcname = _parse_string(context, end=end, auto_escape=["."])
    _expects(context, "(")
    context.pop()
    args = []
    while context.has_more() and not context.match(")"):
        if not context.match("("):
            value = _parse_value(context)
            args.append(value)
        else:
            value = _parse_statement(context)
            args.append(value)

        if context.match(","):
            context.pop()
        else:
            _expects(context, ")")
    _expects(context, ")")
    context.pop()
    return Function(funcname, args)


def _parse_list_construction(context):
    _expects(context, "[")
    context.pop()
    statements = []
    while context.has_more():
        if context.match(" "):
            context.pop()
            continue
        if context.match("]"):
            break
        if context.match("("):
            statement = _parse_statement(context, end=[",", "]"])
            statements.append(statement)
        else:
            value = _parse_value(context)
            statements.append(value)
        if context.match(","):
            context.pop()
    _expects(context, "]")
    context.pop()
    return ListConstruction(statements=statements)


def _parse_selector(context):
    _expects(context, ".")
    context.pop() # pop .
    value = _parse_value(context)
    if type(value) not in [int, str, float]:
        raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Type Error : Unable to use type {0} for selector".format(type(value).__name__))
    return Selector(value)


def _parse_value(context):
    if context.match(["i(", "s(", "f(", "j("]):
        auto_escape = list(SPECIAL_CHARS)
        auto_escape.remove(")")
        value_type = context.next(2)[0]
        index_start = context.index
        if not context.has_more():
            raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected end of query")
        string_value = _parse_string(context, end=[")"], auto_escape=auto_escape)
        _expects(context, ")")
        context.pop(1)
        value = string_value
        if value_type == "i":
            try:
                value = int(string_value)
            except ValueError:
                raise JSTQLParserException(query_string=context.query_string, index=index_start, message="Type Error : Unable to parse {0} as int".format(string_value))
        elif value_type == "f":
            try:
                value = float(string_value)
            except ValueError:
                raise JSTQLParserException(query_string=context.query_string, index=index_start, message="Type Error : Unable to parse {0} as float".format(string_value))
        elif value_type == "j":
            try:
                value = json.loads(string_value)
                if type(value) not in (dict, list):
                    raise JSTQLParserException(query_string=query_string, index=index_start, message="Type Error : Unknown type {0} after parsing a json type".format(type(value)))
            except ValueError:
                raise JSTQLParserException(query_string=context.query_string, index=index_start, message="Type Error : Unable to parse {0} as json-type".format(string_value))
        return value
    else:
        string_value = _parse_string(context, end=SPECIAL_CHARS)
        value = string_value
        for t in [int, float]:
            try:
                value = t(string_value)
                break
            except ValueError as e:
                pass
        return value


def _parse_string(context, end=None, escape_char=None, auto_escape=None):
    start_index = context.index
    end = end or []
    string = []
    auto_escape = auto_escape or []
    escape_char = escape_char if escape_char and len(escape_char) == 1 else "~"
    while context.has_more() and context.peek(1) not in end:
        if context.match([escape_char]):
            context.pop()
            if context.has_more():
                string.append(context.next())
            else:
                raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Unexpected end of string")
        if context.match(list(SPECIAL_CHARS)) and not context.match(auto_escape):
            raise JSTQLParserException(query_string=query_string, index=index, message="Unescaped special character '{0}'".format(query_string[index]))
        else:
            string.append(context.next())

    return "".join(string)


def _parse_iterator(context):
    _expects(context, ".[")
    context.pop(1)

    if not context.has_more():
        raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected end of query")
    if context.match("[*]"):
        context.pop(3)
        return Iterator(value="*")
    context.pop()

    left_value, right_value, single_select = None, None, False

    if context.match(":") : #takes care of [:X]
        context.pop()
        start_index = context.index
        right_value = _parse_value(context)
        if right_value and not isinstance(right_value, int):
            raise JSTQLParserException(query_string=context.query_string, index=start_index, message="Unable to use type {0} for list iteration".format(type(right_value).__name__))
    else:
        left_value = _parse_value(context)
        if left_value and not isinstance(left_value, int):
            raise JSTQLParserException(query_string=context.query_string, index=start_index, message="Unable to use type {0} for list iteration".format(type(left_value).__name__))

        if not context.has_more():
            raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected end of query")

        if context.match(":"): # takes care of [X:..]
            context.pop()
            if not context.has_more():
                raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected end of query")
            if not context.match("]") : # takes care of [X:Y]
                right_value = _parse_value(context)
                if right_value and not isinstance(right_value, int):
                    raise JSTQLParserException(query_string=context.query_string, index=start_index, message="Unable to use type {0} for list iteration".format(type(right_value).__name__))
        elif context.match("]"): # takes care of [X]
            single_select = True

    if not context.has_more():
        raise JSTQLParserException(query_string=context.query_string, index=context.index, message="Syntax Error : Unexpected end of query")

    _expects(context, "]")
    context.pop() # pop ]

    if single_select:
        return Selector(value=left_value)
    return Iterator(value=(left_value, right_value))


def _parse_assignment(context, assignment_target, end=None):
    end = end or []
    context.pop() # pop =
    if context.match("("):
        rhs = _parse_statement(context, end)
    else:
        rhs = _parse_value(context)
    return Assignment(assignment_target, rhs)

############################################# Runtime Stuffs ##########################################################

class RuntimeContext(object):
    """
    A runtime context stores the current state of the json and the original json as well as
    a mutable copy of it.

    It also store a reference to the previous context.
    """

    def __init__(self, data, parent=None, mdata=None, selector=None):
        self.data = data
        self.mdata = mdata # if no mdata is present means this is not in copying mode.
        self.parent = parent
        self.selector = selector

    def copy(self):
        return RuntimeContext(data=self.data, mdata=self.mdata)

    def select(self, value):
        if isinstance(self.data, list):
            if isinstance(value, int):
                try:
                    return RuntimeContext(
                            data=self.data[value],
                            mdata=self.mdata[value] if self.mdata else None,
                            parent=self,
                            selector=value
                    )
                except IndexError:
                    raise JSTQLRuntimeException(current_state=self.data, message="Runtime Error : Index out of bound {0}".format(value))
            else:
                raise JSTQLRuntimeException(current_state=self.data, message="Runtime Error : Unable to access list index with {0}".format(value))

        elif isinstance(self.data, dict):
            try:
                return RuntimeContext(
                        data=self.data[value],
                        mdata=self.mdata[value] if self.mdata else None,
                        parent=self,
                        selector=value
                )
            except KeyError:
                raise JSTQLRuntimeException(current_state=self.data, message="Runtime Error : unable to find key {0}".format(value))
        raise JSTQLRuntimeException(current_state=self.data, message="Runtime Error : selecting from type {0} using key {1} is not allowed".format(type(self.data).__name__, value))

    def can_iterate(self):
        return isinstance(self.data, (list, dict))

    @property
    def origin(self):
        temp = self
        while temp.parent is not None:
            temp = temp.parent
        return temp


def run_query(data, query):
    if isinstance(query, PipedStatement):
        current_data = data
        for statement in query.statements:
            current_data = run_query(current_data, statement)
        return current_data
    elif len(query.commands) == 0:
        return data
    else: # normal statement
        # check if there is a need to provide mdata
        if type(query.commands[-1]) in [Assignment, FunctionChain]:
            context = RuntimeContext(data=data, mdata=recursive_copy(data))
        else:
            context = RuntimeContext(data=data)
        return _run_commands(query.commands, context)


def _run_commands(commands, context, allow_modifier=True):

    # if modifier is not allowed but is modifier, raise exception
    if not allow_modifier and type(commands[-1]) in [Assignment, FunctionChain]:
        raise ModifierNotAllowed()

    index = 0
    while index < len(commands)-1:
        command = commands[index]
        if isinstance(command, Selector):
            context = context.select(command.value)
        elif isinstance(command, Iterator):
            if not context.can_iterate():
                raise JSTQLRuntimeException(context.data, message="Unable to iterate object of type {0}".format(type(context.data).__name))
            if type(commands[-1]) in [Assignment, FunctionChain]:
                if isinstance(context.data, list):
                    for i in range(0, len(context.data)):
                        _run_commands(commands[index+1:], context.select(i), allow_modifier=allow_modifier)
                    return context.origin.mdata
                else:
                    for key, value in context.data.items():
                        _run_commands(commands[index+1:], context.select(key), allow_modifier=allow_modifier)
                    return context.origin.mdata
            else:
                if isinstance(context.data, list):
                    output = [ _run_commands(commands[index+1:], context.select(i)) for i in range(0, len(context.data)) ]
                    return output
                else:
                    output = { key: _run_commands(commands[index+1:], context.select(key)) for key in context.data.keys() }
                    return output
        else:
            raise JSTQLException(message="Unable to run command of type {0}".format(type(command).__name__))
        index+=1

    command = commands[-1]
    if isinstance(command, Selector):
        context = context.select(command.value)
        return context.data

    elif isinstance(command, Iterator):
        if isinstance(context.data, list):
            if command.value == "*":
                return context.data
            elif command.value[0] is None:
                return context.data[:command.value[1]]
            elif command.value[1] is None:
                return context.data[command.value[0]:]
            else:
                return context.data[command.value[0]:command.value[1]]
        elif isinstance(context.data, dict):
            if command.value == "*":
                return context.data
            else:
                raise JSTQLRuntimeException(context.data, message="Unable to iterate object of type {0}".format(type(context.data).__name))
        else:
            raise JSTQLRuntimeException(context.data, message="Unable to iterate object of type {0}".format(type(context.data).__name))

    elif isinstance(command, Assignment):
        if type(command.value) in [int, str, dict, list, float]:
            value = command.value
        elif isinstance(command.value, Statement):
            try:
                value = _run_commands(command.value.commands, RuntimeContext(data=context.data, mdata=None, parent=context.parent), allow_modifier=False)
            except ModifierNotAllowed as m:
                raise JSTQLException("Right hand side of assignment cannot be a modifier statement")
        context.mdata[command.selector.value] = value
        return context.origin.mdata

    elif isinstance(command, FunctionChain):
        import extensions # only import when we are running
        function_class = None
        for ind, function in enumerate(command.functions):
            if function.name not in extensions.registered_functions:
                raise JSTQLException("Function {0} not found".format(function.name))
            function_class = extensions.registered_functions[function.name]

            if type(context.mdata) not in function_class.allowed_context:
                raise JSTQLRuntimeException(current_state=context.mdata,
                        message="Function {0} cannot be applied to type {1}".format(function.name, type(context.mdata).__name__))

            input_args = []
            for arg in function.args:
                if isinstance(arg, Command):
                    if not isinstance(arg, Statement):
                        raise JSTQLException(message="Command of {0} cannot be used as function arguments".format(type(arg).__name__))
                    try:
                        arg = _run_commands(arg.commands, context.parent, allow_modifier=False)
                    except ModifierNotAllowed as m:
                        raise JSTQLException("Function argument cannot be a modifier")
                input_args.append(arg)
            data = function_class.run(context, *input_args)
            if not function_class.is_modifier:
                if ind != len(command.functions) - 1:
                    raise JSTQLRuntimeException(current_state=context.mdata,
                            message="Non modifier function {0} must be the last command".format(function.name))
                else:
                    return data

            if not context.parent:
                context.mdata = data
            else:
                context.parent.mdata[context.selector] = data

        return context.origin.mdata
    elif isinstance(command, ListConstruction):
        return [ _run_commands(statement.commands, context, allow_modifier=False) for statement in command.statements ]
