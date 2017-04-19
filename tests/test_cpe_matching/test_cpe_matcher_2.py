import unittest

from pymongo import MongoClient
from local_repositories.cpe_dict import IVA_CPE_COLLECTION
from tests.mock_config import patch_config_for, DB_HOST, DB_PORT, IVA_DB_NAME

CPE1 = {"uri_binding" : "cpe:/a:microsoft:visual_foxpro:9.0:sp1", "formatted_string_binding" : "cpe:2.3:a:microsoft:visual_foxpro:9.0:sp1", "wfn" : { "part" : "a", "product" : "visual_foxpro", "sw_edition" : "ANY", "target_sw" : "ANY", "language" : "ANY", "update" : "sp1", "vendor" : "microsoft", "edition" : "ANY", "version" : "9.0", "other" : "ANY", "target_hw" : "ANY" } }
CPE2 = {"uri_binding" : "cpe:/a:microsoft:visual_studio:97", "formatted_string_binding" : "cpe:2.3:a:microsoft:visual_studio:97", "wfn" : {"part" : "a", "product" : "visual_studio", "sw_edition" : "ANY", "target_sw" : "ANY", "language" : "ANY", "update" : "ANY", "vendor" : "microsoft", "edition" : "ANY", "version" : "97", "other" : "ANY", "target_hw" : "ANY"}}
CPE3 = {"uri_binding" : "cpe:/a:microsoft:visual_c%2b%2b:-", "formatted_string_binding" : "cpe:2.3:a:microsoft:visual_c%2b%2b", "wfn" : {"part" : "a", "product" : "visual_c++", "sw_edition" : "ANY", "target_sw" : "ANY", "language" : "ANY", "update" : "ANY", "vendor" : "microsoft", "edition" : "ANY", "version" : "NA", "other" : "ANY", "target_hw" : "ANY"}}
CPE4 = {"uri_binding" : "cpe:/a:microsoft:visual_c%2b%2b:2002", "formatted_string_binding" : "cpe:2.3:a:microsoft:visual_c%2b%2b:2002", "wfn" : {"part" : "a", "product" : "visual_c++", "sw_edition" : "ANY", "target_sw" : "ANY", "language" : "ANY", "update" : "ANY", "vendor" : "microsoft", "edition" : "ANY", "version" : "2002", "other" : "ANY", "target_hw" : "ANY"}}
CPE5 = {"uri_binding" : "cpe:/a:microsoft:visual_c%23:-", "formatted_string_binding" : "cpe:2.3:a:microsoft:visual_c%23", "wfn" : { "vendor" : "microsoft", "product" : "visual_c#", "sw_edition" : "ANY", "target_hw" : "ANY", "update" : "ANY", "edition" : "ANY", "other" : "ANY", "target_sw" : "ANY", "language" : "ANY", "part" : "a", "version" : "NA" } }
CPE6 = {"uri_binding" : "cpe:/a:oracle:jre:1.4.2_38", "wfn" : { "product" : "jre", "edition" : "ANY", "part" : "a", "sw_edition" : "ANY", "target_hw" : "ANY", "other" : "ANY", "language" : "ANY", "version" : "1.4.2_38", "update" : "ANY", "vendor" : "oracle", "target_sw" : "ANY" }, "formatted_string_binding" : "cpe:2.3:a:oracle:jre:1.4.2_38" }
CPE7 = {"uri_binding" : "cpe:/a:oracle:jre:1.5.0:update_40", "wfn" : { "product" : "jre", "edition" : "ANY", "part" : "a", "sw_edition" : "ANY", "target_hw" : "ANY", "other" : "ANY", "language" : "ANY", "version" : "1.5.0", "update" : "update_40", "vendor" : "oracle", "target_sw" : "ANY" }, "formatted_string_binding" : "cpe:2.3:a:oracle:jre:1.5.0:update_40" }
CPE8 = {"uri_binding" : "cpe:/a:oracle:jdk:1.4.2_40", "wfn" : { "product" : "jdk", "edition" : "ANY", "part" : "a", "sw_edition" : "ANY", "target_hw" : "ANY", "other" : "ANY", "language" : "ANY", "version" : "1.4.2_40", "update" : "ANY", "vendor" : "oracle", "target_sw" : "ANY" }, "formatted_string_binding" : "cpe:2.3:a:oracle:jdk:1.4.2_40" }
CPE9 = {"uri_binding" : "cpe:/a:oracle:jdk:1.5.0:update_36", "wfn" : { "product" : "jdk", "edition" : "ANY", "part" : "a", "sw_edition" : "ANY", "target_hw" : "ANY", "other" : "ANY", "language" : "ANY", "version" : "1.5.0", "update" : "update_36", "vendor" : "oracle", "target_sw" : "ANY" }, "formatted_string_binding" : "cpe:2.3:a:oracle:jdk:1.5.0:update_36" }

SOFTWARE = {"version": "9.0.21022", "product" : "Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022", "id" : "f7b5ca72b77093679e0832a748a38620", "cpe" : None, "vendor" : "Microsoft Corporation", "cve_matches" : [ ] }
SOFTWARE_JRE = {"id": "c32db0ee26a06a438538a157fddeb909", "vendor" : "Oracle Corporation", "product" : "Java 8 Update 112", "cpe" : None, "cve_matches" : [ ], "version" : "8.0.1120.15" }
SOFTWARE_JDK = {"id": "2609fe77e378a4396a82282fe51696de", "vendor" : "Oracle Corporation", "product" : "Java SE Development Kit 8 Update 112", "cpe" : None, "cve_matches" : [ ], "version" : "8.0.1120.15" }
SOFTWARE_JAVA_UPDATER = {"id": "3a850a96a1c11a1e8756f743dd0ec57c", "vendor" : "Oracle Corporation", "product" : "Java Auto Updater", "cpe" : None, "cve_matches" : [ ], "version" : "2.8.121.13" }


class TestCPEMatcher2(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.test_db_collection = self.test_db[IVA_CPE_COLLECTION]
        self.test_db_collection.insert_many(documents=[CPE1, CPE2, CPE3, CPE4, CPE5, CPE6, CPE7, CPE8, CPE9])
        self.create_cpe_matcher_obj()

    def create_cpe_matcher_obj(self):
        self.cpe_matcher = patch_config_for('matching.cpe_matcher', 'CPEMatcher')

    def test_search_cpe_candidates_for_software(self):
        cpe_candidates = self.cpe_matcher.search_cpes_for_software(SOFTWARE)
        self.assertEqual(3, len(cpe_candidates))
        self.assertEqual(CPE3.get('uri_binding'), cpe_candidates[0].get('uri_binding'))
        self.assertEqual(CPE4.get('uri_binding'), cpe_candidates[1].get('uri_binding'))
        self.assertEqual(CPE5.get('uri_binding'), cpe_candidates[2].get('uri_binding'))

    def test_search_cpe_candidates_for_jre(self):
        cpe_candidates = self.cpe_matcher.search_cpes_for_software(SOFTWARE_JRE)
        self.assertEqual(2, len(cpe_candidates))
        self.assertEqual(CPE6.get('uri_binding'), cpe_candidates[0].get('uri_binding'))
        self.assertEqual(CPE7.get('uri_binding'), cpe_candidates[1].get('uri_binding'))

    def test_search_cpe_candidates_for_jdk(self):
        cpe_candidates = self.cpe_matcher.search_cpes_for_software(SOFTWARE_JDK)
        self.assertEqual(4, len(cpe_candidates))
        self.assertEqual(CPE8.get('uri_binding'), cpe_candidates[0].get('uri_binding'))
        self.assertEqual(CPE9.get('uri_binding'), cpe_candidates[1].get('uri_binding'))
        self.assertEqual(CPE6.get('uri_binding'), cpe_candidates[2].get('uri_binding'))
        self.assertEqual(CPE7.get('uri_binding'), cpe_candidates[3].get('uri_binding'))

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
