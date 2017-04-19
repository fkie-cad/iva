import unittest
from copy import copy
from alerts.alerts import ALERTS_DB_COLLECTION
from inventory.inventory import INVENTORY_DB_COLLECTION
from tests.dict_tester import DictTester
from pymongo import MongoClient
from tests.mock_config import *

SOFTWARE_ID = 'bdzjhf65g48j1w786454jnm8'
URI_BINDING = 'cpe:/a:1024cms:1024_cms:0.7'
NEW_URI_BINDING = 'cpe:/a:1025cms:1025_cms:0.7'
WFN = {'part': 'a', 'vendor': '1024cms', 'product': '1024_cms', 'version': '0.7', 'update': 'ANY', 'edition': 'ANY',
       'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'}
MODIFIED_WFN = {'part': 'a', 'vendor': '1025cms', 'product': '1025_cms', 'version': '0.7', 'update': 'ANY',
                'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY',
                'language': 'ANY'}
CPE_DOC = {'uri_binding': URI_BINDING, 'wfn': WFN}
CVE_MATCHES = [{'cve_id': 'CVE-2016-1256'}, {'cve_id': 'CVE-2016-1257'}]


class TestCPEInventory(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.inventory_collection = self.test_db[INVENTORY_DB_COLLECTION]
        self.alert_collection = self.test_db[ALERTS_DB_COLLECTION]
        self.dict_tester = DictTester()
        self.create_software_cpe_obj()

    def create_software_cpe_obj(self):
        self.cpe_inventory = patch_config_for('inventory.software_cpe', 'SoftwareCPE')

    def test_create_cpe_inventory_document(self):
        # call method being tested
        document = self.cpe_inventory.create_sw_cpe_dict(WFN)

        # verify
        self.dict_tester.assertEqualKeys(CPE_DOC, document)
        self.dict_tester.assertEqualValues(CPE_DOC, document)

    def test_assign_cpe_to_software(self):
        # insert software
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'version': '', 'product': '', 'vendor': '',
                                              'cpe': None,
                                              'cve_matches': []})

        # assign cpe to software
        cpe = {'uri_binding': URI_BINDING, 'wfn': WFN}
        self.cpe_inventory.assign_cpe_to_software(cpe, SOFTWARE_ID)

        # verify
        software = self.inventory_collection.find_one({'id': SOFTWARE_ID})
        self.assertEqual(cpe, software.get('cpe'))

    def test_update_software_cpe(self):
        # insert software which CPE will be updated
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'version': '', 'product': '', 'vendor': '',
                                              'cpe': CPE_DOC,
                                              'cve_matches': []})

        # update CPE
        self.cpe_inventory.update_software_cpe(SOFTWARE_ID, MODIFIED_WFN)

        # verify update
        software = self.inventory_collection.find_one({'id': SOFTWARE_ID})
        updated_cpe = software.get('cpe')
        self.assertIsNotNone(updated_cpe)
        self.assertEqual(NEW_URI_BINDING, updated_cpe.get('uri_binding'))
        self.dict_tester.assertEqualKeys(MODIFIED_WFN, updated_cpe.get('wfn'))
        self.dict_tester.assertEqualValues(MODIFIED_WFN, updated_cpe.get('wfn'))

    def test_update_software_cpe_removes_cve_matches(self):
        # insert software
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'version': '', 'product': '', 'vendor': '',
                                              'cpe': CPE_DOC,
                                              'cve_matches': CVE_MATCHES})

        # update CPE
        self.cpe_inventory.update_software_cpe(SOFTWARE_ID, MODIFIED_WFN)

        # verify cve_matches were removed
        software = self.inventory_collection.find_one({'id': SOFTWARE_ID})
        self.assertEqual(0, len(software.get('cve_matches')))

    def test_update_software_cpe_changes_alert_status_to_removed(self):
        # insert software
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'version': '', 'product': '', 'vendor': '',
                                              'cpe': CPE_DOC,
                                              'cve_matches': CVE_MATCHES})

        # insert alert
        self.alert_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                          'cves': ['CVE-2016-1256', 'CVE-2016-1257'],
                                          'status': 'new', 'log': [''], 'notes': ''})

        # update CPE
        self.cpe_inventory.update_software_cpe(SOFTWARE_ID, MODIFIED_WFN)

        # verify alert status was changed to removed
        alert = self.alert_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertEqual('removed', alert.get('status'))

    def test_get_software_cpe_by_id(self):
        # insert software
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'version': '', 'product': '', 'vendor': '',
                                              'cpe': CPE_DOC,
                                              'cve_matches': []})
        self.assertEqual(CPE_DOC, self.cpe_inventory.get_software_cpe_by_id(SOFTWARE_ID))

    def test_get_software_cpe_by_id_returns_none(self):
        self.assertIsNone(self.cpe_inventory.get_software_cpe_by_id('dsd'))

    def test_get_software_cpe_by_uri_binding(self):
        # insert software
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'version': '', 'product': '', 'vendor': '',
                                              'cpe': CPE_DOC,
                                              'cve_matches': []})
        self.assertEqual(CPE_DOC, self.cpe_inventory.get_software_cpe_by_uri(URI_BINDING))

    def test_get_software_cpe_by_uri_binding_returns_none(self):
        self.assertIsNone(self.cpe_inventory.get_software_cpe_by_uri('dsdsdf'))

    def insert_cpe_item(self):
        self.inventory_collection.insert_one(copy(CPE_DOC))

    def insert_alert(self):
        self.alert_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                          'cves': ['cve1', 'cve2', 'cve3'], 'status': 'new', 'log': [''], 'notes': ''})

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()

if __name__ == '__main__':
    unittest.main()
