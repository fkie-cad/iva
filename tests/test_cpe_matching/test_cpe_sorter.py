import unittest

from matching.cpe_sorter import *

unsorted_cpes = [{'wfn': {'version': '4.0', 'target_sw': 'android_marshmallow'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.0:beta:~~~android_marshmallow~~'},
                 {'wfn': {'version': '1.0.1.2', 'target_sw': 'android_marshmallow'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:1.0.1.2:beta'},
                 {'wfn': {'version': '4.1.2', 'target_sw': 'ANY'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.1.2:beta'},
                 {'wfn': {'version': '4.6.3', 'target_sw': 'windows'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.6.3:beta:~~~windows~~'},
                 {'wfn': {'version': '4.7.1', 'target_sw': 'android'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.7.1:beta:~~~android~~'},
                 {'wfn': {'version': '4.7.2', 'target_sw': 'ANY'},
                  'uri_binding':'cpe:/a:string_value_with\:double_points:internet_explorer:4.7.2:beta'},
                 {'wfn': {'version': '4.3.2', 'target_sw': 'linux'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.3.2:beta:~~~linux~~'},
                 {'wfn': {'version': '2.3.1', 'target_sw': 'linux'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:2.3.1:beta'},
                 {'wfn': {'version': '4.7.3', 'target_sw': 'mac_os_x'},
                  'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.7.3:beta:~~~mac_os_x~~'}
                 ]


unsorted_cpes_year = [{'wfn': {'version': '2000', 'target_sw': 'android_marshmallow'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:2000:beta:~~~android_marshmallow~~'},
                      {'wfn': {'version': '2007', 'target_sw': 'android_marshmallow'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:2007:beta'},
                      {'wfn': {'version': '4.1.2', 'target_sw': 'ANY'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.1.2:beta'},
                      {'wfn': {'version': '2010', 'target_sw': 'windows'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:2010:beta:~~~windows~~'},
                      {'wfn': {'version': '4.7.1', 'target_sw': 'android'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.7.1:beta:~~~android~~'},
                      {'wfn': {'version': '2001', 'target_sw': 'ANY'},
                       'uri_binding':'cpe:/a:string_value_with\:double_points:internet_explorer:2001:beta'},
                      {'wfn': {'version': '4.3.2', 'target_sw': 'linux'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.3.2:beta:~~~linux~~'},
                      {'wfn': {'version': '2010', 'target_sw': 'linux'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:2010:beta'},
                      {'wfn': {'version': '4.7.3', 'target_sw': 'mac_os_x'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:4.7.3:beta:~~~mac_os_x~~'},
                      {'wfn': {'version': '2010', 'target_sw': 'mac_os_x'},
                       'uri_binding': 'cpe:/a:string_value_with\:double_points:internet_explorer:2010:beta:~~~mac_os_x~~'}]

version = '4.7.2'
version_without_points = '4_7-2'
version_year = '2010'

os_windows = 'windows_7'
os_linux = 'linux_ubuntu'
os_android = 'android'
os_mac = 'mac_os_x_10.11'


class TestCPESorter(unittest.TestCase):

    def test_sort_cpes_by_software_version(self):
        sorted_cpes = sort_cpes_by_version(unsorted_cpes, version)

        self.assertEqual(len(unsorted_cpes), len(sorted_cpes))
        self.assertEqual(unsorted_cpes[5], sorted_cpes[0])   # 4.7.2
        self.assertEqual(unsorted_cpes[4], sorted_cpes[1])   # 4.7.1
        self.assertEqual(unsorted_cpes[8], sorted_cpes[2])   # 4.7.3
        self.assertEqual(unsorted_cpes[0], sorted_cpes[3])   # 4.0
        self.assertEqual(unsorted_cpes[2], sorted_cpes[4])   # 4.1.2
        self.assertEqual(unsorted_cpes[3], sorted_cpes[5])   # 4.6.3
        self.assertEqual(unsorted_cpes[6], sorted_cpes[6])   # 4.3.2

    def test_cpes_and_sorted_cpes_are_equal_when_software_version_not_splitted_by_points(self):
        sorted_cpes = sort_cpes_by_version(unsorted_cpes, version_without_points)
        self.assertListEqual(unsorted_cpes, sorted_cpes)

    def test_sort_cpes_by_version_with_year(self):
        sorted_cpes = sort_cpes_by_version(unsorted_cpes_year, version_year)
        self.assertEqual(len(unsorted_cpes_year), len(sorted_cpes))
        self.assertEqual(unsorted_cpes_year[3], sorted_cpes[0])   # 2010
        self.assertEqual(unsorted_cpes_year[7], sorted_cpes[1])   # 2010
        self.assertEqual(unsorted_cpes_year[9], sorted_cpes[2])   # 2010
        self.assertEqual(unsorted_cpes_year[0], sorted_cpes[3])   # 2000
        self.assertEqual(unsorted_cpes_year[1], sorted_cpes[4])   # 2007
        self.assertEqual(unsorted_cpes_year[5], sorted_cpes[5])   # 2001

    def test_sort_cpes_by_operating_system_windows(self):
        sorted_cpes = sort_cpes_by_operating_system(unsorted_cpes, os_windows)
        self.assertEqual(len(unsorted_cpes), len(sorted_cpes))
        self.assertEqual(unsorted_cpes[3], sorted_cpes[0])

    def test_sort_cpes_by_operating_system_linux(self):
        sorted_cpes = sort_cpes_by_operating_system(unsorted_cpes, os_linux)
        self.assertEqual(len(unsorted_cpes), len(sorted_cpes))
        self.assertEqual(unsorted_cpes[6], sorted_cpes[0])

    def test_sort_cpes_by_operating_system_android(self):
        sorted_cpes = sort_cpes_by_operating_system(unsorted_cpes, os_android)
        self.assertEqual(len(unsorted_cpes), len(sorted_cpes))
        self.assertEqual(unsorted_cpes[4], sorted_cpes[0])
        self.assertEqual(unsorted_cpes[0], sorted_cpes[1])


if __name__ == '__main__':
    unittest.main()
