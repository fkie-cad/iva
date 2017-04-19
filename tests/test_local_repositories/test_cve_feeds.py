import unittest
from copy import copy
from pymongo import MongoClient
from tests.mock_config import *
from local_repositories.cve_search import CVE_SEARCH_CVE_COLLECTION
from local_repositories.cve_feeds import IVA_CVE_COLLECTION, BATCH_SIZE
from tests.dict_tester import DictTester

cve_search_cve1 = {"cvss": 5, "Modified": "2008-09-09T08:33:31.007Z", "access": {"complexity": "LOW", "vector": "NETWORK", "authentication": "NONE"},
                   "references": ["http://www.microsoft.com/technet/security/bulletin/ms98-008.asp"], "Published" : "1997-12-16T00:00:00Z",
                   "impact": {"availability": "PARTIAL", "integrity": "NONE", "confidentiality": "NONE"}, "cvss-time": "2004-01-01T00:00:00Z",
                   "vulnerable_configuration": ["cpe:2.3:a:hp:dtmail", "cpe:2.3:a:university_of_washington:pine:4.02", "cpe:2.3:o:sco:unixware:7.0"], "id": "CVE-1999-0004",
                   "vulnerable_configuration_cpe_2_2": ["cpe:/a:hp:dtmail", "cpe:/a:university_of_washington:pine:4.02", "cpe:/o:sco:unixware:7.0"],
                   "summary": "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook."}
cve_search_cve2 = {"cvss": 6, "Modified": "2008-09-09T08:33:31.007Z", "access": {"complexity": "LOW", "vector": "NETWORK", "authentication": "NONE"},
                   "references": ["http://www.microsoft.com/technet/security/bulletin/ms98-008.asp"], "Published" : "1997-12-16T00:00:00Z",
                   "impact": {"availability": "PARTIAL", "integrity": "NONE", "confidentiality": "NONE"}, "cvss-time": "2004-01-01T00:00:00Z",
                   "vulnerable_configuration": ["cpe:2.3:a:hp:dtmail", "cpe:2.3:a:university_of_washington:pine:4.02", "cpe:2.3:o:sco:unixware:7.0"], "id": "CVE-2000-0005",
                   "vulnerable_configuration_cpe_2_2": ["cpe:/a:hp:dtmail", "cpe:/a:university_of_washington:pine:4.02", "cpe:/o:sco:unixware:7.0"],
                   "summary": "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook."}
cve_search_cve3 = {"cvss": 7, "Modified": "2008-09-09T08:33:31.007Z", "access": {"complexity": "LOW", "vector": "NETWORK", "authentication": "NONE"},
                   "references": ["http://www.microsoft.com/technet/security/bulletin/ms98-008.asp"], "Published" : "1997-12-16T00:00:00Z",
                   "impact": {"availability": "PARTIAL", "integrity": "NONE", "confidentiality": "NONE"}, "cvss-time": "2004-01-01T00:00:00Z",
                   "vulnerable_configuration": ["cpe:2.3:a:hp:dtmail", "cpe:2.3:a:university_of_washington:pine:4.02", "cpe:2.3:o:sco:unixware:7.0"], "id": "CVE-2001-0006",
                   "vulnerable_configuration_cpe_2_2": ["cpe:/a:hp:dtmail", "cpe:/a:university_of_washington:pine:4.02", "cpe:/o:sco:unixware:7.0"],
                   "summary": "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook."}

iva_cve1 = {"cpe_entries": [{"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "ANY",
                                     "target_sw": "ANY", "vendor": "hp", "product": "dtmail",
                                     "edition": "ANY", "language": "ANY", "part": "a", "update": "ANY",
                                     "other": "ANY"}, "uri_binding": "cpe:/a:hp:dtmail"},
                            {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "7.0",
                                     "target_sw": "ANY", "vendor": "sco", "product": "unixware",
                                     "edition": "ANY", "language": "ANY", "part": "o", "update": "ANY",
                                     "other": "ANY"}, "uri_binding": "cpe:/o:sco:unixware:7.0"},
                            {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "4.02", "target_sw": "ANY",
                                     "vendor": "university_of_washington", "product": "pine", "edition": "ANY",
                                     "language": "ANY", "part": "a", "update": "ANY", "other": "ANY"},
                             "uri_binding": "cpe:/a:university_of_washington:pine:4.02"}],
            "cve_summary": "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook.",
            "cve_id": "CVE-1999-0004"}
iva_cve2 = {"cpe_entries": [{"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "ANY",
                                     "target_sw": "ANY", "vendor": "hp", "product": "dtmail",
                                     "edition": "ANY", "language": "ANY", "part": "a", "update": "ANY",
                                     "other": "ANY"}, "uri_binding": "cpe:/a:hp:dtmail"},
                            {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "7.0",
                                     "target_sw": "ANY", "vendor": "sco", "product": "unixware",
                                     "edition": "ANY", "language": "ANY", "part": "o", "update": "ANY",
                                     "other": "ANY"}, "uri_binding": "cpe:/o:sco:unixware:7.0"},
                            {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "4.02", "target_sw": "ANY",
                                     "vendor": "university_of_washington", "product": "pine", "edition": "ANY",
                                     "language": "ANY", "part": "a", "update": "ANY", "other": "ANY"},
                             "uri_binding": "cpe:/a:university_of_washington:pine:4.02"}],
            "cve_summary": "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook.",
            "cve_id": "CVE-2000-0005"}
iva_cve3 = {"cpe_entries": [{"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "ANY",
                                     "target_sw": "ANY", "vendor": "hp", "product": "dtmail",
                                     "edition": "ANY", "language": "ANY", "part": "a", "update": "ANY",
                                     "other": "ANY"}, "uri_binding": "cpe:/a:hp:dtmail"},
                            {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "7.0",
                                     "target_sw": "ANY", "vendor": "sco", "product": "unixware",
                                     "edition": "ANY", "language": "ANY", "part": "o", "update": "ANY",
                                     "other": "ANY"}, "uri_binding": "cpe:/o:sco:unixware:7.0"},
                            {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "4.02", "target_sw": "ANY",
                                     "vendor": "university_of_washington", "product": "pine", "edition": "ANY",
                                     "language": "ANY", "part": "a", "update": "ANY", "other": "ANY"},
                             "uri_binding": "cpe:/a:university_of_washington:pine:4.02"}],
            "cve_summary": "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook.",
            "cve_id": "CVE-2001-0006"}


class TestCVEFeeds(unittest.TestCase):

    def setUp(self):
        self.create_mongodb_client()
        self.create_collections()
        self.create_cve_db_object()

    def create_cve_db_object(self):
        self.cve_feeds = patch_config_for('local_repositories.cve_feeds', 'CVEFeeds')

    def test_update_cves_feeds_when_iva_cve_collection_is_empty(self):
        # insert CVE entries in cve-search database
        self.insert_cves_in_cve_search_db()
        # call method being tested
        self.cve_feeds.update_cve_feeds()
        # verify that CVE entries were read from cve-search database and inserted in IVA
        # database according to the IVA format
        self.verify_update()

    def test_update_cve_feeds_when_iva_cve_collection_is_not_empty(self):
        # insert CVE entries in cve-search database
        self.insert_cves_in_cve_search_db()
        # insert CVE entries in IVA database
        self.iva_cves_collection.insert_many(documents=[copy(iva_cve1), copy(iva_cve2)])
        # call method being tested
        self.cve_feeds.update_cve_feeds()
        # verify that CVE entries were read from cve-search database and inserted in IVA
        # database according to the IVA format
        self.verify_update()

    def test_update_batch_size(self):
        for i in range(BATCH_SIZE + 5):
            cve = copy(cve_search_cve1)
            cve.update({'id': i})
            self.cve_search_cves_collection.insert_one(cve)
        self.cve_feeds.update_cve_feeds()
        self.assertEqual(self.iva_cves_collection.count(), BATCH_SIZE + 5)

    def verify_update(self):
        dict_tester = DictTester()
        updated_cves = self.get_updated_cves()
        dict_tester.assertEqualKeys(iva_cve1, updated_cves[0])
        dict_tester.assertEqualKeys(iva_cve2, updated_cves[1])
        dict_tester.assertEqualKeys(iva_cve3, updated_cves[2])
        self.assertEqual(iva_cve1.get('cve_id'), updated_cves[2].get('cve_id'))
        self.assertEqual(iva_cve2.get('cve_id'), updated_cves[1].get('cve_id'))
        self.assertEqual(iva_cve3.get('cve_id'), updated_cves[0].get('cve_id'))
        self.assertEqual(3, self.iva_cves_collection.count())

    def get_updated_cves(self):
        cves = list(self.iva_cves_collection.find())
        for cve in cves:
            cve.pop('_id')
        return cves

    def create_mongodb_client(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)

    def create_collections(self):
        self.iva_db = self.mongodb_client[IVA_DB_NAME]
        self.cve_search_db = self.mongodb_client[CVE_SEARCH_DB_NAME]
        self.cve_search_cves_collection = self.cve_search_db[CVE_SEARCH_CVE_COLLECTION]
        self.iva_cves_collection = self.iva_db[IVA_CVE_COLLECTION]

    def insert_cves_in_cve_search_db(self):
        bulk = self.cve_search_cves_collection.initialize_ordered_bulk_op()
        bulk.insert(cve_search_cve1)
        bulk.insert(cve_search_cve2)
        bulk.insert(cve_search_cve3)
        bulk.execute()
        pass

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.drop_database(CVE_SEARCH_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
