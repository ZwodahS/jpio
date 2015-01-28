
from jstql import *
from . import CommonTestCase

class ParserTestCase(CommonTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def _run_test(self, query, expectation):
        try:
            q = parse(query)
            self.assertEqual(type(q), Statement)
            self.assertEqual(len(q.commands), len(expectation["expected_types"]))
            self._basic_test(q.commands, **expectation)
        except JSTQLParserException as e:
            self.assertFalse(expectation.get("success", True))

    def _basic_test(self, commands, expected_types, expected_values, expected_keys):
        for expected_type, expected_value, expected_key, command in zip(expected_types, expected_values, expected_keys, commands):
            self.assertEqual(expected_type, type(command));
            self.assertEqual(expected_value, getattr(command, expected_key, None))

    def test_empty_query(self):
        query = ""
        q = parse(query)
        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 0)

    def test_single_selector(self):
        query = ".hello"
        expectation = dict(
                expected_types=[Selector],
                expected_values=["hello"],
                expected_keys=["value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_double_selector(self):
        query = ".hello.world"
        expectation = dict(
                expected_types=[Selector, Selector],
                expected_values=["hello", "world"],
                expected_keys=["value", "value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_int_auto_casting(self):
        query = ".hello.1"
        expectation = dict(
                expected_types=[Selector, Selector],
                expected_values=["hello", 1],
                expected_keys=["value", "value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_float_selector(self):
        query = ".hello.f(3.142)"
        expectation = dict(
                expected_types=[Selector, Selector],
                expected_values=["hello", 3.142],
                expected_keys=["value", "value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_json_selector_will_fail(self):
        query = '.j({"hello":1})'
        expectation = dict(
                expected_types=[],
                expected_values=[],
                expected_keys=[],
                success=False
        )
        self._run_test(query=query, expectation=expectation)

    #################### Test iterator #####################

    def test_list_selector(self):
        query = ".[1]"
        expectation = dict(
                expected_types=[Selector],
                expected_values=[1],
                expected_keys=["value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_list_range_full(self):
        query = '.[3:4]'
        expectation = dict(
                expected_types=[Iterator],
                expected_values=[(3,4)],
                expected_keys=["value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_list_range_left(self):
        query = ".[3:]"
        expectation = dict(
                expected_types=[Iterator],
                expected_values=[(3, None)],
                expected_keys=["value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_list_range_right(self):
        query = ".[:4]"
        expectation = dict(
                expected_types=[Iterator],
                expected_values=[(None, 4)],
                expected_keys=["value"]
        )
        self._run_test(query=query, expectation=expectation)

    def test_list_select_all(self):
        query = ".[*]"
        expectation = dict(
                expected_types=[Iterator],
                expected_values=["*"],
                expected_keys=["value"]
        )
        self._run_test(query=query, expectation=expectation)

    #################### Test assignment ####################
    def test_single_assignment(self):
        query = ".world=hello"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 1)
        assignment = q.commands[0]

        self.assertEqual(assignment.selector.value, "world")
        self.assertEqual(assignment.value, "hello")

    def test_assignment_to_selector(self):
        query = ".hello=(.world)"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 1)
        assignment = q.commands[0]

        self.assertEqual(assignment.selector.value, "hello")
        self.assertEqual(type(assignment.value), Statement)

        rhs_statement = assignment.value

        self.assertEqual(len(rhs_statement.commands), 1)
        self.assertEqual(type(rhs_statement.commands[0]), Selector)
        self.assertEqual(rhs_statement.commands[0].value, "world")

    #################### Test pipe ####################

    def test_pipe(self):
        query = ".world|.hello"
        q = parse(query)

        self.assertEqual(type(q), PipedStatement)
        self.assertEqual(len(q.statements), 2)

        statement1 = q.statements[0]
        self._basic_test(statement1.commands, [Selector], ["world"], ["value"])

        statement2 = q.statements[1]
        self._basic_test(statement2.commands, [Selector], ["hello"], ["value"])

    #################### Test function chain ####################

    def test_single_function(self):
        query = ".world#sort()"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 2)

        command1 = q.commands[0]
        command2 = q.commands[1]

        self.assertEqual(type(command1), Selector)
        self.assertEqual(command1.value, "world")

        self.assertEqual(type(command2), FunctionChain)
        self.assertEqual(len(command2.functions), 1)

        function1 = command2.functions[0]
        self.assertEqual(type(function1), Function)
        self.assertEqual(function1.name, "sort")
        self.assertEqual(len(function1.args), 0)

    def test_function_chain(self):
        query = ".world#sort()#reversed()"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 2)

        command1 = q.commands[0]
        command2 = q.commands[1]

        self.assertEqual(type(command1), Selector)
        self.assertEqual(command1.value, "world")

        self.assertEqual(type(command2), FunctionChain)
        self.assertEqual(len(command2.functions), 2)

        function1 = command2.functions[0]
        self.assertEqual(type(function1), Function)
        self.assertEqual(function1.name, "sort")
        self.assertEqual(len(function1.args), 0)

        function2 = command2.functions[1]
        self.assertEqual(type(function2), Function)
        self.assertEqual(function2.name, "reversed")
        self.assertEqual(len(function2.args), 0)

    def test_function_args(self):
        query = ".world#del(key)"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 2)

        command1 = q.commands[0]
        command2 = q.commands[1]

        self.assertEqual(type(command1), Selector)
        self.assertEqual(command1.value, "world")

        self.assertEqual(type(command2), FunctionChain)
        self.assertEqual(len(command2.functions), 1)

        function1 = command2.functions[0]
        self.assertEqual(type(function1), Function)
        self.assertEqual(function1.name, "del")
        self.assertEqual(len(function1.args), 1)
        self.assertEqual(function1.args[0], "key")

    def test_function_chain_with_args(self):
        query = ".world#del(key)#del(key2,False)"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 2)

        command1 = q.commands[0]
        command2 = q.commands[1]

        self.assertEqual(type(command1), Selector)
        self.assertEqual(command1.value, "world")

        self.assertEqual(type(command2), FunctionChain)
        self.assertEqual(len(command2.functions), 2)

        function1 = command2.functions[0]
        self.assertEqual(type(function1), Function)
        self.assertEqual(function1.name, "del")
        self.assertEqual(len(function1.args), 1)
        self.assertEqual(function1.args[0], "key")

        function2 = command2.functions[1]
        self.assertEqual(type(function2), Function)
        self.assertEqual(function2.name, "del")
        self.assertEqual(len(function2.args), 2)
        self.assertEqual(function2.args[0], "key2")
        self.assertEqual(function2.args[1], "False")

    # def test_selector_in_function(self):
    #     query = ".world#sort()#pop((.count))"
    #     q = parse(query)

    #     self.assertEqual(type(q), Statement)
    #     self.assertEqual(len(q.commands), 2)

    #     command1 = q.commands[0]
    #     command2 = q.commands[1]

    #     self.assertEqual(type(command1), Selector)
    #     self.assertEqual(command1.value, "world")

    #     self.assertEqual(type(command2), FunctionChain)
    #     self.assertEqual(len(command2.functions), 2)

    #     function1 = command2.functions[0]
    #     self.assertEqual(type(function1), Function)
    #     self.assertEqual(function1.name, "sort")
    #     self.assertEqual(len(function1.args), 0)

    #     function2 = command2.functions[1]
    #     self.assertEqual(type(function2), Function)
    #     self.assertEqual(function2.name, "pop")
    #     self.assertEqual(len(function2.args), 1)
    #     args1 = function2.args[0]
    #     self.assertEqual(type(args1), Statement)
    #     self.assertEqual(len(args1.commands), 1)
    #     self.assertEqual(type(args1.commands[0]), Selector)
    #     self.assertEqual(args1.commands[0].value, "count")

    def test_allow_dot_in_function_name(self):
        query = ".world#default.sort()"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 2)

        command1 = q.commands[0]
        command2 = q.commands[1]

        self.assertEqual(type(command1), Selector)
        self.assertEqual(command1.value, "world")

        self.assertEqual(type(command2), FunctionChain)
        self.assertEqual(len(command2.functions), 1)

        function1 = command2.functions[0]
        self.assertEqual(type(function1), Function)
        self.assertEqual(function1.name, "default.sort")
        self.assertEqual(len(function1.args), 0)


    def test_list_construction_with_value(self):
        query = ".world=([1, 2, 3])"
        q = parse(query)

        self.assertEqual(type(q), Statement)
        self.assertEqual(len(q.commands), 1)

        command1 = q.commands[0]

        self.assertEqual(type(command1), Assignment)
        self.assertEqual(type(command1.selector), Selector)
        self.assertEqual(command1.selector.value, "world")
        self.assertEqual(type(command1.value), Statement)
        self.assertEqual(len(command1.value.commands), 1)
        self.assertEqual(type(command1.value.commands[0]), ListConstruction)
