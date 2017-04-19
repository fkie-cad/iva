import unittest
from copy import copy
from pymongo import MongoClient
from local_repositories.cpe_dict import IVA_CPE_COLLECTION
from tests.mock_config import *

CPE1 = {'wfn': {'part': 'a', 'vendor': '1024cms', 'product': '1024_cms', 'version': '0.7', 'update': 'ANY',
                'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY',
                'language': 'ANY'},
        'uri_binding': 'cpe:/a:1024cms:1024_cms:0.7',
        'formatted_string_binding': 'cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*'}

CPE2 = {'wfn': {'part': 'a', 'vendor': '1024cms', 'product': '1024_cms', 'version': '1.7', 'update': 'ANY', 'edition': 'ANY',
                'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'},
        'uri_binding': 'cpe:/a:1024cms:1024_cms:1.7',
        'formatted_string_binding': 'cpe:2.3:a:1024cms:1024_cms:1.7:*:*:*:*:*:*:*'}

CPE3 = {'wfn': {'part': 'a', 'vendor': 'cms_vendor',
                'product': '1024_cms', 'version': '1.7', 'update': 'ANY', 'edition': 'ANY',
                'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'},
        'uri_binding': 'cpe:/a:cms_vendor:1024_cms:1.7',
        'formatted_string_binding': 'cpe:2.3:a:cms_vendor:1024_cms:1.7:*:*:*:*:*:*:*'}
CPE4 = {'wfn': {'part': 'a', 'vendor': 'microsoft',
                'product': '.net_framework', 'version': '1.7', 'update': 'ANY', 'edition': 'ANY',
                'sw_edition': 'ANY', 'target_sw': 'windows', 'target_hw': 'x64', 'other': 'ANY', 'language': 'ANY'},
        'uri_binding': 'cpe:/a:microsoft:.net_framework:1.7',
        'formatted_string_binding': 'cpe:2.3:a:microsoft:.net_framework:1.7:*:*:*:*:*:*:*'}
EXPECTED_CPE_MATCHES = [CPE1, CPE2, CPE3]
SOFTWARE_1 = {'id': 'd6218a56203853300f4862ae8c23a103', 'product': '1024cms 1024-cms', 'vendor': '1024CMS Corporation', 'version': '0.7'}
SOFTWARE_2 = {'id': 'd6218a56203853300f4862ae8c23a103', 'product': 'Product Not Exist', 'vendor': 'Vendor Unknown', 'version': '0'}
SOFTWARE_3 = {'id': 'd6218a56203853300f4862ae8c23a103', 'product': '1024cms0', 'vendor': 'cms_vendor_ld', 'version': '0'}


class TestCPEMatcher(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.test_db_collection = self.test_db[IVA_CPE_COLLECTION]
        self.test_db_collection.insert_many(documents=[copy(CPE1), copy(CPE2), copy(CPE3), copy(CPE4)])
        self.create_cpe_matcher_obj()

    def create_cpe_matcher_obj(self):
        self.cpe_matcher = patch_config_for('matching.cpe_matcher', 'CPEMatcher')

    def test_get_cpe_matches_for_software(self):
        cpe_matches = self.cpe_matcher.search_cpes_for_software(SOFTWARE_1)
        self.assertEqual(2, len(cpe_matches))
        self.assertEqual(EXPECTED_CPE_MATCHES[0], cpe_matches[0])
        self.assertEqual(EXPECTED_CPE_MATCHES[1], cpe_matches[1])

    def test_get_cpe_matches_returns_no_matches(self):
        cpe_matches = self.cpe_matcher.search_cpes_for_software(SOFTWARE_2)
        self.assertEqual(0, len(cpe_matches))

    def test_edit_distance_in_product_and_vendor(self):
        cpe_matches = self.cpe_matcher.search_cpes_for_software(SOFTWARE_3)
        self.assertEqual(1, len(cpe_matches))
        self.assertEqual(CPE3, cpe_matches[0])

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()

if __name__ == '__main__':
    unittest.main()