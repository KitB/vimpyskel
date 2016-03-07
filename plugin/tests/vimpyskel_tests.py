import unittest
import vimpyskel as sut


@unittest.skip("Don't forget to test!")
class VimpyskelTests(unittest.TestCase):

    def test_example_fail(self):
        result = sut.vimpyskel_example()
        self.assertEqual("Happy Hacking", result)
