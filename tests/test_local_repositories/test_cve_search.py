import unittest
from tests.mock_config import *
from local_repositories.cve_search import CVE_SEARCH_CPE_COLLECTION, CVE_SEARCH_CVE_COLLECTION
from pymongo import MongoClient


class TestCVESearchDB(unittest.TestCase):

    def setUp(self):
        self.create_mongodb_client()
        self.create_collections()
        self.create_cve_search_db_object()

    def test_get_number_of_cves_entries_returns_4(self):
        self.insert_cves()
        self.assertEqual(4, self.cve_search_db.get_number_of_cves_entries())

    def test_get_number_of_cves_entries_returns_0(self):
        self.assertEqual(0, self.cve_search_db.get_number_of_cves_entries())

    def test_get_number_of_cpes_entries_returns_4(self):
        self.insert_cpes()
        self.assertEqual(4, self.cve_search_db.get_number_of_cpes_entries())

    def test_get_number_of_cpes_entries_returns_0(self):
        self.assertEqual(0, self.cve_search_db.get_number_of_cpes_entries())

    def test_is_cve_search_populated_returns_true(self):
        self.insert_cpes()
        self.insert_cves()
        self.assertTrue(self.cve_search_db.is_cve_search_populated())

    def test_is_cve_search_populated_returns_false_when_cpe_collection_empty(self):
        self.insert_cves()
        self.assertFalse(self.cve_search_db.is_cve_search_populated())

    def test_is_cve_search_populated_returns_false_when_cve_collection_empty(self):
        self.insert_cpes()
        self.assertFalse(self.cve_search_db.is_cve_search_populated())

    def test_is_cve_search_populated_returns_false(self):
        self.assertFalse(self.cve_search_db.is_cve_search_populated())

    def create_mongodb_client(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)

    def create_collections(self):
        self.cve_search_db = self.mongodb_client[CVE_SEARCH_DB_NAME]
        self.cve_search_cpe_collection = self.cve_search_db[CVE_SEARCH_CPE_COLLECTION]
        self.cve_search_cve_collection = self.cve_search_db[CVE_SEARCH_CVE_COLLECTION]

    def create_cve_search_db_object(self):
        self.cve_search_db = patch_config_for('local_repositories.cve_search', 'CVESearchDB')

    def insert_cves(self):
        self.cve_search_cve_collection.insert_many(documents=[{'id': 'cve1'}, {'id': 'cve2'}, {'id': 'cve3'},
                                                              {'id': 'cve4'}])

    def insert_cpes(self):
        self.cve_search_cpe_collection.insert_many(documents=[{'id': 'cpe1'}, {'id': 'cpe2'}, {'id': 'cpe3'},
                                                              {'id': 'cpe4'}])

    def tearDown(self):
        self.mongodb_client.drop_database(CVE_SEARCH_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
