
from jstql import *
from . import CommonTestCase

class FunctionsTestCase(CommonTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    #### Test List sort ###

    def test_sort_by_value(self):
        data = { "data" : [3, 1, 2] }
        query_string = ".data#sort()"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, { "data" : [1, 2, 3] })

    def test_sort_by_item_value(self):
        data = { "data" : [ { "value" : 3 }, { "value" : 4 }, { "value" : 1 } ] }
        query_string = ".data#sort(value)"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, { "data" : [ { "value" : 1 }, { "value" : 3 }, { "value" : 4 } ] })

    def test_rsort_by_value(self):
        data = { "data" : [3, 1, 2] }
        query_string = ".data#rsort()"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, { "data" : [3, 2, 1] })

    def test_rsort_by_item_value(self):
        data = { "data" : [ { "value" : 3 }, { "value" : 4 }, { "value" : 1 } ] }
        query_string = ".data#rsort(value)"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, { "data" : [ { "value" : 4 }, { "value" : 3 }, { "value" : 1 } ] })

    def test_string_upper(self):
        data = { "data" : "simple_string" }
        query_string = ".data#upper()"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, { "data" : "SIMPLE_STRING" })

    def test_string_lower(self):
        data = { "data" : "SIMPLE_STRING" }
        query_string = ".data#lower()"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, { "data" : "simple_string" })

    def test_string_lower_after_select(self):
        data = { "data" : "SIMPLE_STRING" }
        query_string = ".data|#lower()"
        statement = parse(query_string)
        result = run_query(data, statement)
        self._test_equal(result, "simple_string")


