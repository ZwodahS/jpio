
import unittest

class CommonTestCase(unittest.TestCase):

    def _test_equal(self, d1, d2):
        self.assertEqual(type(d1), type(d2))

        if isinstance(d1, dict):
            set_all = set(list(d1.keys()) + list(d2.keys()))
            for k in set_all:
                if k not in d1 or k not in d2:
                    self.fail("key '{0}' is missing in one of the dictionary. \n {1} \n {2} ".format(k, d1, d2))
                self._test_equal(d1.get(k), d2.get(k))

        elif isinstance(d1, list):
            if len(d1) != len(d2):
                self.fail("length of list is different : {0} , {1}".format(d1, d2))

            for v1, v2 in zip(d1,d2):
                self._test_equal(v1, v2)

        else:
            self.assertEqual(d1, d2)
