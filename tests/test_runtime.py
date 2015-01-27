
from . import CommonTestCase
from jstql import *

class RuntimeTestCase(CommonTestCase):

    def setUp(self):
        self.data = {
            "version" : {
                "major" : 1,
                "minor" : 0,
                "patch" : 0,
            },
            "books" : [
                {
                    "name" : "Introduction to Json",
                    "isbn" : "M19165029",
                    "author" : "1"
                },
                {
                    "name" : "Introduction to Python",
                    "isbn" : "M35123115",
                    "author" : "2"
                },
                {
                    "name" : "Crazy JPIO",
                    "isbn" : "M51236131",
                    "author" : "3"
                },
            ]
        }

    def tearDown(self):
        pass

    def test_empty_accessor(self):
        query_string = ""
        statement = parse(query_string)
        result = run_query(self.data, statement)
        self._test_equal(result, self.data)

    def test_basic_accessor(self):
        query_string = ".version"
        statement = parse(query_string)
        result = run_query(self.data, statement)
        self._test_equal(result, self.data["version"])

    def test_double_accessor(self):
        query_string = ".version.major"
        statement = parse(query_string)
        result = run_query(self.data, statement)
        self._test_equal(result, self.data["version"]["major"])

    def test_list_accessor(self):
        query_string = ".books.[0]"
        statement = parse(query_string)
        result = run_query(self.data, statement)
        self._test_equal(result, self.data["books"][0])

    def test_list_iterator(self):
        query_string = ".books.[*].name"
        statement = parse(query_string)
        result = run_query(self.data, statement)
        expected_result = [ i["name"] for i in self.data["books"] ]
        self._test_equal(result, expected_result)

    def test_assignment(self):
        query_string = ".version.minor=3"
        expected_result = recursive_copy(self.data)
        expected_result["version"]["minor"] = 3
        statement = parse(query_string)
        result = run_query(self.data, statement)
        self._test_equal(result, expected_result)

    def test_mass_assignment(self):
        query_string = ".books.[*].date=s(2014-12-12)"
        expected_result = recursive_copy(self.data)
        for b in expected_result["books"]:
            b["date"] = "2014-12-12"
        statement = parse(query_string)
        result = run_query(self.data, statement)
        print(result)
        self._test_equal(result, expected_result)

    def test_set_by_selection(self):
        query_string = ".books.[*].date=(.author)"
        expected_result = recursive_copy(self.data)
        for b in expected_result["books"]:
            b["date"] = b["author"]
        statement = parse(query_string)
        result = run_query(self.data, statement)
        print(result)
        self._test_equal(result, expected_result)

