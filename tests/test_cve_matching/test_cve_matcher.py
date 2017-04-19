import unittest
from copy import copy
from pymongo import MongoClient
from local_repositories.cve_feeds import IVA_CVE_COLLECTION
from matching.cve_matcher import are_strings_similar, is_version_any, get_main_version
from tests.dict_tester import DictTester
from tests.mock_config import *
from inventory.inventory import INVENTORY_DB_COLLECTION


CVE_1 = {'cve_id': 'CVE-2017-0000',
         'cve_summary': 'Adobe Connect before 95.2 allows remote attackers to spoof the user interface.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:vendor:product:9.5', 'wfn': {'part': 'a', 'vendor': 'vendor',
                                                                              'product': 'product',
                                                                              'version': '9',
                                                                              'update': 'ANY', 'edition': 'ANY',
                                                                              'language': 'ANY', 'sw_edition': 'ANY',
                                                                              'target_sw': 'ANY',
                                                                              'target_hw': 'ANY',
                                                                              'other': 'ANY'}}]}

CVE_2 = {'cve_id': 'CVE-2017-0001',
         'cve_summary': 'Adobe Connect before 95.2 allows remote attackers to spoof the user interface.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:vendor:product:9.3', 'wfn': {'part': 'a', 'vendor': 'vendor',
                                                                              'product': 'product',
                                                                              'version': '9.3',
                                                                              'update': 'ANY', 'edition': 'ANY',
                                                                              'language': 'ANY', 'sw_edition': 'ANY',
                                                                              'target_sw': 'ANY',
                                                                              'target_hw': 'ANY',
                                                                              'other': 'ANY'}},
                         {'uri_binding': 'cpe:/a:no_match:no_match:9.3', 'wfn': {'part': 'a', 'vendor': 'no_match',
                                                                                 'product': 'no_match',
                                                                                 'version': '9.3',
                                                                                 'update': 'ANY', 'edition': 'ANY',
                                                                                 'language': 'ANY', 'sw_edition': 'ANY',
                                                                                 'target_sw': 'ANY',
                                                                                 'target_hw': 'ANY',
                                                                                 'other': 'ANY'}}]}

CVE_3 = {'cve_id': 'CVE-2017-0002',
         'cve_summary': 'ldjzeoq 73n32 435jv product jduanvctz vendor',
         'cpe_entries': []}


CVE_4 = {'cve_id': 'CVE-2017-0003',
         'cve_summary': 'Adobe Connect before 95.2 allows remote attackers to spoof the user interface.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:adobe:reader:9.5', 'wfn': {'part': 'a', 'vendor': 'adobe',
                                                                            'product': 'reader',
                                                                            'version': '9.5',
                                                                            'update': 'ANY', 'edition': 'ANY',
                                                                            'language': 'ANY', 'sw_edition': 'ANY',
                                                                            'target_sw': 'ANY',
                                                                            'target_hw': 'ANY',
                                                                            'other': 'ANY'}}]}


CVE_5 = {'cve_id': 'CVE-2017-0004',
         'cve_summary': 'Adobe Connect before 95.2 allows remote attackers to spoof the user interface.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:adobe:adobe_reader:9.5', 'wfn': {'part': 'a', 'vendor': 'adobe',
                                                                                  'product': 'adobe_reader',
                                                                                  'version': '9.5',
                                                                                  'update': 'ANY', 'edition': 'ANY',
                                                                                  'language': 'ANY', 'sw_edition': 'ANY',
                                                                                  'target_sw': 'ANY',
                                                                                  'target_hw': 'ANY',
                                                                                  'other': 'ANY'}}]}

CVE_6 = {'cve_id': 'CVE-2017-0005',
         'cve_summary': 'Adobe Connect before 95.2 allows remote attackers to spoof the user interface.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:adobe:reader_adobe:9.5', 'wfn': {'part': 'a', 'vendor': 'adobe',
                                                                                  'product': 'reader_adobe',
                                                                                  'version': '9.5',
                                                                                  'update': 'ANY', 'edition': 'ANY',
                                                                                  'language': 'ANY', 'sw_edition': 'ANY',
                                                                                  'target_sw': 'ANY',
                                                                                  'target_hw': 'ANY',
                                                                                  'other': 'ANY'}}]}


CVE_7 = {'cve_id': 'CVE-2017-0006',
         'cve_summary': '',
         'cpe_entries': [{'uri_binding': 'cpe:/a:adobe:reader_adobe:9.5', 'wfn': {'part': 'a', 'vendor': 'adobe',
                                                                                  'product': 'reader_adobe',
                                                                                  'version': '9.5.6',
                                                                                  'update': 'ANY', 'edition': 'ANY',
                                                                                  'language': 'ANY', 'sw_edition': 'ANY',
                                                                                  'target_sw': 'ANY',
                                                                                  'target_hw': 'ANY',
                                                                                  'other': 'ANY'}},
                         {'uri_binding': 'cpe:/a:adobe:reader_adobe:9.5', 'wfn': {'part': 'a', 'vendor': 'adobe',
                                                                                  'product': 'reader_adobe',
                                                                                  'version': '9.5',
                                                                                  'update': 'ANY', 'edition': 'ANY',
                                                                                  'language': 'ANY', 'sw_edition': 'ANY',
                                                                                  'target_sw': 'ANY',
                                                                                  'target_hw': 'ANY',
                                                                                  'other': 'ANY'}}]}


class TestCVEMatcher(unittest.TestCase):

    def setUp(self):
        self.dict_tester = DictTester()
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.iva_cve_collection = self.test_db[IVA_CVE_COLLECTION]
        self.iva_inventory_collection = self.test_db[INVENTORY_DB_COLLECTION]
        self.insert_cves()
        self.insert_sw_inventory()
        self.create_cve_matcher_obj()

    def create_cve_matcher_obj(self):
        self.cve_matcher = patch_config_for('matching.cve_matcher', 'CVEMatcher')

    def test_search_cves_for_cpe_returns_three_matches(self):
        matches = self.cve_matcher.search_cves_for_cpe('cpe:/a:vendor:product:9.5')
        self.assertEqual(3, len(matches))

        self.assertTrue(CVE_1 in matches)
        self.assertEqual(CVE_2.get('cve_id'), matches[1].get('cve_id'))
        self.assertTrue(CVE_3 in matches)
        self.assertEqual(1, len(matches[1].get('cpe_entries')))

    def test_search_cves_for_cpe_returns_when_cve_cpe_product_has_vendor(self):
        matches = self.cve_matcher.search_cves_for_cpe('cpe:/a:adobe:reader:9.5')
        self.assertEqual(4, len(matches))
        self.assertTrue(CVE_4 in matches)
        self.assertTrue(CVE_5 in matches)
        self.assertTrue(CVE_6 in matches)

    def test_search_cves_for_cpe_when_cpe_product_has_vendor(self):
        matches = self.cve_matcher.search_cves_for_cpe('cpe:/a:adobe:adobe_reader:9.5')
        self.assertEqual(2, len(matches))
        self.assertTrue(CVE_4 in matches)
        self.assertTrue(CVE_5 in matches)

    def test_search_cves_for_cpe_when_cpe_product_has_typo(self):
        matches = self.cve_matcher.search_cves_for_cpe('cpe:/a:vendor:produc:9.5')
        self.assertEqual(3, len(matches))

    def insert_cves(self):
        self.iva_cve_collection.insert_many(documents=[copy(CVE_1), copy(CVE_2), copy(CVE_3), copy(CVE_4), copy(CVE_5),
                                                       copy(CVE_6), copy(CVE_7)])

    def insert_sw_inventory(self):
        self.iva_inventory_collection.insert_one({'cpe': {'wfn': {'product': 'product', 'vendor': 'vendor'}}})
        self.iva_inventory_collection.insert_one({'cpe': {'wfn': {'product': 'reader', 'vendor': 'adobe'}}})
        self.iva_inventory_collection.insert_one({'cpe': {'wfn': {'product': 'adobe_reader', 'vendor': 'adobe'}}})

    def test_compare_words_edit_distance_returns_true(self):
        self.assertTrue(are_strings_similar('abcd', 'abdc'))
        self.assertTrue(are_strings_similar('abcd', 'abcc'))
        self.assertTrue(are_strings_similar('abcd', 'accc'))
        self.assertTrue(are_strings_similar('microsoft', 'microsott'))
        self.assertTrue(are_strings_similar('microsoft', 'macrosott'))
        self.assertTrue(are_strings_similar('microsoft', 'macrosof'))
        self.assertTrue(are_strings_similar('microsoft', 'macrosot'))

    def test_compare_words_edit_distance_returns_false(self):
        self.assertFalse(are_strings_similar('abcd', 'axxx'))
        self.assertFalse(are_strings_similar('abcd', 'cccc'))
        self.assertFalse(are_strings_similar('abcd', 'xjkh'))
        self.assertFalse(are_strings_similar('abcdabcdabcdab', 'abcdabcdabcdabcdabcdab1154ds'))
        self.assertFalse(are_strings_similar('microsoft', 'macrosotx'))

    def test_is_version_any(self):
        self.assertTrue(is_version_any({'version': 'ANY'}))
        self.assertTrue(is_version_any({'version': '*'}))
        self.assertFalse(is_version_any({'version': '15315'}))

    def test_get_main_version(self):
        self.assertEqual('1', get_main_version({'version': '1.5.86'}))
        self.assertEqual('2007', get_main_version({'version': '2007'}))
        self.assertEqual('ANY', get_main_version({'version': 'ANY'}))

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
