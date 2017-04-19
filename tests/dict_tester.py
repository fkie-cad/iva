import unittest


class DictTester(unittest.TestCase):

    def assertEqualKeys(self, dict1, dict2):
        keys_dict1 = self.getSortedKeys(dict1)
        keys_dict2 = self.getSortedKeys(dict2)
        self.assertEqual(keys_dict1, keys_dict2)

    def assertEqualValues(self, dict1, dict2):
        for key, value_dict1 in dict1.items():
            self.assertEqual(value_dict1, dict2[key], "key: " + key + " values not equal " + str(value_dict1) + " != " + str(dict2[key]))

    def getSortedKeys(self, report):
        return sorted(report.keys())