
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
