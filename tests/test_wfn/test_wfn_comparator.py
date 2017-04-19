import unittest
from wfn.wfn_comparator import compare_wfn
from tests.dict_tester import DictTester


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.dict_tester = DictTester()

    def test_compare_wfn_returns_100_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        result = compare_wfn(wfn_a, wfn_a)
        # verify
        expected_result = {'coincidence_rate': 100, 'not_matches': []}
        self.dict_tester.assertEqualKeys(expected_result, result)
        self.dict_tester.assertEqualValues(expected_result, result)

    def test_compare_wfn_returns_0_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe_', 'product': 'connect_', 'version': '9.5.', 'update': '-',
                 'edition': '-', 'language': '-', 'sw_edition': '-', 'target_sw': '-', 'target_hw': '-',
                 'other': '-'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['vendor', 'product', 'version', 'update', 'edition', 'language', 'sw_edition', 'target_sw',
                       'target_hw', 'other']
        self.assertEqual(0, result.get('coincidence_rate'))
        self.assertListEqual(sorted(not_matches), sorted(result.get('not_matches')))

    def test_compare_wfn_returns_40_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5.', 'update': '-',
                 'edition': '-', 'language': '-', 'sw_edition': '-', 'target_sw': '-', 'target_hw': '-',
                 'other': '-'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['version', 'update', 'edition', 'language', 'sw_edition', 'target_sw', 'target_hw', 'other']
        self.assertEqual(40, result.get('coincidence_rate'))
        self.assertListEqual(sorted(not_matches), sorted(result.get('not_matches')))

    def test_compare_wfn_returns_55_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '-',
                 'edition': '-', 'language': '-', 'sw_edition': '-', 'target_sw': '-', 'target_hw': '-',
                 'other': '-'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['update', 'edition', 'language', 'sw_edition', 'target_sw', 'target_hw', 'other']
        self.assertEqual(55, result.get('coincidence_rate'))
        self.assertListEqual(sorted(not_matches), sorted(result.get('not_matches')))

    def test_compare_wfn_returns_75_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '-', 'sw_edition': '-', 'target_sw': '-', 'target_hw': '-',
                 'other': '-'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['language', 'sw_edition', 'target_sw', 'target_hw', 'other']
        self.assertEqual(75, result.get('coincidence_rate'))
        self.assertListEqual(sorted(not_matches), sorted(result.get('not_matches')))

    def test_compare_wfn_returns_95_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'u96',
                 'edition': '2016', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'u96',
                 'edition': '2016', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '-'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['other']
        self.assertEqual(95, result.get('coincidence_rate'))
        self.assertListEqual(sorted(not_matches), sorted(result.get('not_matches')))

    def test_compare_wfn_returns_25_percent_of_coincidence(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe_', 'product': 'connect_', 'version': '9.5.', 'update': 'u96_',
                 'edition': '2016_', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY',
                 'other': 'ANY'}
        wfn_b = {'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'u96',
                 'edition': '2016', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['vendor', 'product', 'version', 'update', 'edition']
        self.assertEqual(25, result.get('coincidence_rate'))
        self.assertListEqual(sorted(not_matches), sorted(result.get('not_matches')))

    def test_compare_wfn_any_case(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'u96',
                 'edition': '2016', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY',
                 'other': 'ANY'}
        wfn_b = {'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'u96',
                 'edition': '2016', 'language': 'DE', 'sw_edition': '2015', 'target_sw': 'windows', 'target_hw': 'x85',
                 'other': 'bla'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        self.assertEqual(100, result.get('coincidence_rate'))
        self.assertEqual([], result.get('not_matches'))

        # ANY value with asterisk
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5.2', 'update': 'u96',
                 'edition': '2016', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        not_matches = ['version']
        self.assertEqual(85, result.get('coincidence_rate'))
        self.assertListEqual(not_matches, result.get('not_matches'))

        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'u96',
                 'edition': '2016', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.5', 'update': 'ANY',
                 'edition': 'ANY', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY',
                 'other': '-'}
        result = compare_wfn(wfn_a, wfn_b)
        # verify  ANY is not equal to -
        not_matches = ['other']
        self.assertEqual(95, result.get('coincidence_rate'))
        self.assertListEqual(not_matches, result.get('not_matches'))

        wfn_b.update({'other': 'NA'})
        # verify ANY is not equal to NA
        not_matches = ['other']
        self.assertEqual(95, result.get('coincidence_rate'))
        self.assertListEqual(not_matches, result.get('not_matches'))

    def test_compare_wfn_version_equal(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.*', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.*'})
        wfn_b.update({'version': '9.1.5'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.2.3.4'})
        wfn_b.update({'version': '9.*'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.2.3.4'})
        wfn_b.update({'version': '9.1.*'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.2.3.4'})
        wfn_b.update({'version': '9.1.2.*'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.2.3.4'})
        wfn_b.update({'version': '9.1.2.3.*'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.*'})
        wfn_b.update({'version': '9.1.2.3.*'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.2.3.*'})
        wfn_b.update({'version': '9.1.*'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.*.2.3'})
        wfn_b.update({'version': '9.9.2.3'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '2008'})
        wfn_b.update({'version': '2008'})
        self.compare_and_verify_equal_version(wfn_a, wfn_b)

    def compare_and_verify_equal_version(self, wfn_a, wfn_b):
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        self.assertEqual(100, result.get('coincidence_rate'))
        self.assertListEqual([], result.get('not_matches'))

    def test_compare_wfn_version_not_equal(self):
        wfn_a = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9.1.*', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        wfn_b = {'part': 'a', 'vendor': 'adobe', 'product': 'connect', 'version': '9', 'update': '*',
                 'edition': '*', 'language': '*', 'sw_edition': '*', 'target_sw': '*', 'target_hw': '*',
                 'other': '*'}
        self.compare_and_verify_not_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.2.3.4.*'})
        wfn_b.update({'version': '9.1.*'})
        self.compare_and_verify_not_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.1.*'})
        wfn_b.update({'version': '9.2.3.4.*'})
        self.compare_and_verify_not_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.*.1.3'})
        wfn_b.update({'version': '9.5.1.2'})
        self.compare_and_verify_not_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.*.1.3'})
        wfn_b.update({'version': '9.5.1.3.8'})
        self.compare_and_verify_not_equal_version(wfn_a, wfn_b)

        wfn_a.update({'version': '9.*.1.3.8.9'})
        wfn_b.update({'version': '9.*.1.3.8'})
        self.compare_and_verify_not_equal_version(wfn_a, wfn_b)

    def compare_and_verify_not_equal_version(self, wfn_a, wfn_b):
        result = compare_wfn(wfn_a, wfn_b)
        # verify
        self.assertEqual(85, result.get('coincidence_rate'))
        self.assertListEqual(['version'], result.get('not_matches'))


if __name__ == '__main__':
    unittest.main()
