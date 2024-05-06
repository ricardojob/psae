import unittest

class TestCallForFunctions(unittest.TestCase):

    def test_simple(self):
        result_value = 4
        expect_value = 4
        self.assertEqual(result_value, expect_value)

if __name__ == '__main__':
    unittest.main()