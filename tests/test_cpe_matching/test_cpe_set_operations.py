import unittest
from matching import cpe_set_operations

cpe1 = {'wfn': {'part': 'a', 'vendor': '1024cms', 'product': '1024_cms', 'version': '0.7', 'update': 'ANY',
                'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY',
                'language': 'ANY'},
        'uri_binding': 'cpe:/a:1024cms:1024_cms:0.7',
        'formatted_string_binding': 'cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*'}

cpe2 = {'wfn': {'part': 'a', 'vendor': '1024cms', 'product': '1024_cms', 'version': '1.7', 'update': 'ANY', 'edition': 'ANY',
                'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'},
        'uri_binding': 'cpe:/a:1024cms:1024_cms:1.7',
        'formatted_string_binding': 'cpe:2.3:a:1024cms:1024_cms:1.7:*:*:*:*:*:*:*'}

cpe3 = {'wfn': {'part': 'a', 'vendor': 'cms_vendor',
                'product': '1024_cms', 'version': '1.7', 'update': 'ANY', 'edition': 'ANY',
                'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'},
        'uri_binding': 'cpe:/a:cms_vendor:1024_cms:1.7',
        'formatted_string_binding': 'cpe:2.3:a:cms_vendor:1024_cms:1.7:*:*:*:*:*:*:*'}

cpe4 = {'wfn': {'part': 'a', 'vendor': 'microsoft',
                'product': '.net_framework', 'version': '1.7', 'update': 'ANY', 'edition': 'ANY',
                'sw_edition': 'ANY', 'target_sw': 'windows', 'target_hw': 'x64', 'other': 'ANY', 'language': 'ANY'},
        'uri_binding': 'cpe:/a:microsoft:.net_framework:1.7',
        'formatted_string_binding': 'cpe:2.3:a:microsoft:.net_framework:1.7:*:*:*:*:*:*:*'}

cpes_list_a = [cpe1, cpe2, cpe4]
cpes_list_b = [cpe1, cpe3, cpe4]
cpes_list_c = [cpe3]


class TestCPESetOperations(unittest.TestCase):

    def test_calculate_intersection_between_two_cpe_lists(self):
        intersection_set = cpe_set_operations.calculate_intersection_between_two_cpe_lists(cpes_list_a, cpes_list_b)
        self.assertEqual(2, len(intersection_set))
        self.assertTrue(cpe1 in intersection_set)
        self.assertFalse(cpe2 in intersection_set)
        self.assertFalse(cpe3 in intersection_set)
        self.assertTrue(cpe4 in intersection_set)

        intersection_set = cpe_set_operations.calculate_intersection_between_two_cpe_lists(cpes_list_c, cpes_list_b)
        self.assertEqual(1, len(intersection_set))
        self.assertTrue(cpe3 in intersection_set)

        intersection_set = cpe_set_operations.calculate_intersection_between_two_cpe_lists(cpes_list_c, cpes_list_a)
        self.assertEqual(0, len(intersection_set))

    def test_calculate_symmetric_difference_between_two_cpe_lists(self):
        difference_set = cpe_set_operations.calculate_symmetric_difference_between_two_cpe_lists(cpes_list_a, cpes_list_b)
        self.assertEqual(2, len(difference_set))
        self.assertFalse(cpe1 in difference_set)
        self.assertTrue(cpe2 in difference_set)
        self.assertTrue(cpe3 in difference_set)
        self.assertFalse(cpe4 in difference_set)

if __name__ == '__main__':
    unittest.main()
