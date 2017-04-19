import unittest
from pymongo import MongoClient
from tests.mock_config import *
from local_repositories.cpe_dict import IVA_CPE_COLLECTION
from local_repositories.cve_search import CVE_SEARCH_CPE_COLLECTION


cve_search_cpe1 = {"id": "cpe:2.3:a:%240.99_kindle_books_project:%240.99_kindle_books:6:-:-:-:-:android",
                   "references": ["https://play.google.com/store/apps/details?id=com.kindle.books.for99"],
                   "cpe_2_2": "cpe:/a:%240.99_kindle_books_project:%240.99_kindle_books:6::~~~android~~",
                   "title": "$0.99 Kindle Books project $0.99 Kindle Books (aka com.kindle.books.for99) for android 6.0"}
cve_search_cpe2 = {"id": "cpe:2.3:a:1024cms:1024_cms:0.7", "cpe_2_2": "cpe:/a:1024cms:1024_cms:0.7",
                   "title": "1024cms.org 1024 CMS 0.7"}
cve_search_cpe3 = {"id": "cpe:2.3:a:1024cms:1024_cms:1.2.5", "cpe_2_2": "cpe:/a:1024cms:1024_cms:1.2.5",
                   "title": "1024cms.org 1024 CMS 1.2.5"}

iva_cpe1 = {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "6", "target_sw": "android",
                    "vendor": "$0.99_kindle_books_project", "product": "$0.99_kindle_books", "edition": "ANY",
                    "language": "ANY", "part": "a", "update": "ANY", "other": "ANY"},
            "formatted_string_binding": "cpe:2.3:a:%240.99_kindle_books_project:%240.99_kindle_books:6:-:-:-:-:android",
            "uri_binding": "cpe:/a:%240.99_kindle_books_project:%240.99_kindle_books:6::~~~android~~"}
iva_cpe2 = {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "0.7", "target_sw": "ANY", "vendor": "1024cms",
                    "product": "1024_cms", "edition": "ANY", "language": "ANY", "part": "a", "update": "ANY", "other": "ANY"},
            "formatted_string_binding": "cpe:2.3:a:1024cms:1024_cms:0.7",
            "uri_binding": "cpe:/a:1024cms:1024_cms:0.7"}
iva_cpe3 = {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "1.2.5", "target_sw": "ANY",
                    "vendor": "1024cms", "product": "1024_cms", "edition": "ANY", "language": "ANY", "part": "a",
                    "update": "ANY", "other": "ANY"},
            "formatted_string_binding": "cpe:2.3:a:1024cms:1024_cms:1.2.5",
            "uri_binding": "cpe:/a:1024cms:1024_cms:1.2.5"}


class TestCPEDict(unittest.TestCase):

    def setUp(self):
        self.create_mongodb_client()
        self.create_collections()
        self.fill_search_cve_cpe_collection()
        self.create_cpe_db_object()

    def create_cpe_db_object(self):
        self.cpe_db = patch_config_for('local_repositories.cpe_dict', 'CPEDict')

    def test_update_iva_cpes_collection(self):
        self.cpe_db.update_cpe_dict()
        self.verify_update()

    def test_update_iva_cpes_collection_when_collection_already_updated(self):
        self.cpe_db.update_cpe_dict()
        self.cpe_db.update_cpe_dict()
        self.verify_update()

    def verify_update(self):
        iva_cpes = self.get_iva_cpes()
        self.assertTrue(iva_cpe1 in iva_cpes)
        self.assertTrue(iva_cpe2 in iva_cpes)
        self.assertTrue(iva_cpe3 in iva_cpes)
        self.assertEqual(3, self.iva_cpe_collection.count())

    def get_iva_cpes(self):
        cpes = list(self.iva_cpe_collection.find())
        for cpe in cpes:
            cpe.pop('_id')
        return cpes

    def create_mongodb_client(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)

    def create_collections(self):
        self.iva_db = self.mongodb_client[IVA_DB_NAME]
        self.cve_search_db = self.mongodb_client[CVE_SEARCH_DB_NAME]
        self.cve_search_cpe_collection = self.cve_search_db[CVE_SEARCH_CPE_COLLECTION]
        self.iva_cpe_collection = self.iva_db[IVA_CPE_COLLECTION]

    def fill_search_cve_cpe_collection(self):
        bulk = self.cve_search_cpe_collection.initialize_ordered_bulk_op()
        bulk.insert(cve_search_cpe1)
        bulk.insert(cve_search_cpe2)
        bulk.insert(cve_search_cpe3)
        bulk.execute()

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.drop_database(CVE_SEARCH_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
