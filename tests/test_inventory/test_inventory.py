import hashlib
import unittest
from copy import copy
from tests.mock_config import *
from pymongo import MongoClient
from tests.dict_tester import DictTester
from inventory.inventory import Inventory, INVENTORY_DB_COLLECTION, generate_software_id

SOFTWARE_ID = 'dtr8ewg4af5dz9uj'
NEW_SOFTWARE_1 = {'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu'}
NEW_SOFTWARE_2 = {'version': '0.6.35-0ubuntu7.1', 'product': 'accountsservice', 'vendor': None}
NEW_SOFTWARE_3 = {'version': '8.0.7601.17514', 'product': 'Internet Explorer', 'vendor': 'Microsoft Corporation'}
NEW_SOFTWARE_4 = {'version': '4.5.51209', 'product': 'Microsoft .NET Framework 4.5.2', 'vendor': 'Microsoft Corporation'}
NEW_SOFTWARE_5 = {'version': '9.0.21022', 'product': 'Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022',
                  'vendor': 'Microsoft Corporation'}
GLPI_DB_ITEMS = [NEW_SOFTWARE_1, NEW_SOFTWARE_2, NEW_SOFTWARE_3, NEW_SOFTWARE_4, NEW_SOFTWARE_5]


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.inventory_collection = self.test_db[INVENTORY_DB_COLLECTION]
        self.dict_tester = DictTester()
        self.create_inventory_object()

    def create_inventory_object(self):
        self.inventory = patch_config_for('inventory.inventory', 'Inventory')

    def test_insert_new_software(self):
        new_software = {'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu'}
        self.inventory.insert_software_in_db(new_software)

        # verify if item inserted
        software_id = self.generate_expected_software_id(new_software)
        expected = {'id': software_id, 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                    'cpe': None, 'cve_matches': []}
        new_inserted_software = self.inventory_collection.find_one({'id': software_id}, {'_id': 0})
        self.assertIsNotNone(new_inserted_software)
        self.dict_tester.assertEqualKeys(expected, new_inserted_software)
        self.dict_tester.assertEqualValues(expected, new_inserted_software)

    def test_insert_new_software_to_db_does_not_insert_duplicates(self):
        new_software = {'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu'}
        self.inventory.insert_software_in_db(copy(new_software))
        self.inventory.insert_software_in_db(copy(new_software))

        # verify that only 1 item was inserted
        self.assertEqual(1, self.inventory_collection.count())

    def test_generate_software_id(self):
        self.assertEqual(self.generate_expected_software_id(NEW_SOFTWARE_3), generate_software_id(NEW_SOFTWARE_3))
        self.assertEqual(self.generate_expected_software_id(NEW_SOFTWARE_2), generate_software_id(NEW_SOFTWARE_2))

    def test_get_inventory(self):
        # mock insert inventory in db
        software_1 = {'id': '1', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        software_2 = {'id': '2', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': [{'cve_id': 'CVE-2005-0509', 'positive': 0, 'removed': 0}]}
        software_3 = {'id': '3', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': {'uri_binding': '', 'wfn': {}}, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get inventory
        inventory = self.inventory.get_inventory()

        # verify
        self.assertEqual(3, len(inventory))

    def test_get_software_products_with_assigned_cpe_returns_one_product(self):
        # mock insert inventory in db
        software_1 = {'id': '1', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        software_2 = {'id': '2', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': [{'cve_id': 'CVE-2005-0509', 'positive': 0, 'removed': 0}]}
        software_3 = {'id': '3', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': {'uri_binding': '', 'wfn': {}}, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get items
        software_with_cpe = self.inventory.get_software_products_with_assigned_cpe()

        # verify
        self.assertEqual(1, len(software_with_cpe))

    def test_get_software_products_with_assigned_cpe_returns_empty_list(self):
        # mock insert inventory in db
        software_1 = {'id': '1', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        software_2 = {'id': '2', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': [{'cve_id': 'CVE-2005-0509', 'positive': 0, 'removed': 0}]}
        software_3 = {'id': '3', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get items
        software_with_cpe = self.inventory.get_software_products_with_assigned_cpe()

        # verify
        self.assertEqual(0, len(software_with_cpe))

    def test_get_software_products_without_assigned_cpe_returns_two_products(self):
        # mock insert inventory in db
        software_1 = {'id': '1', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        software_2 = {'id': '2', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': [{'cve_id': 'CVE-2005-0509', 'positive': 0, 'removed': 0}]}
        software_3 = {'id': '3', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': {'uri_binding': '', 'wfn': {}}, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get items
        software_without_cpe = self.inventory.get_software_products_without_assigned_cpe()

        # verify
        self.assertEqual(2, len(software_without_cpe))

    def test_get_software_products_without_assigned_cpe_returns_three_products(self):
        # mock insert inventory in db
        software_1 = {'id': '1', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        software_2 = {'id': '2', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        software_3 = {'id': '3', 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice', 'vendor': 'Ubuntu',
                      'cpe': None, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get items
        software_without_cpe = self.inventory.get_software_products_without_assigned_cpe()

        # verify
        self.assertEqual(3, len(software_without_cpe))

    def test_get_software_without_assigned_cpe_order_by_vendor(self):
        # mock insert items and assign cpe
        item = copy(NEW_SOFTWARE_1)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        item = copy(NEW_SOFTWARE_2)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        item = copy(NEW_SOFTWARE_3)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        item = copy(NEW_SOFTWARE_4)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        item = copy(NEW_SOFTWARE_5)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        items = self.inventory.get_software_products_without_assigned_cpe()

        # verify
        self.assertTrue('Microsoft' in str(items[0].get('vendor')))
        self.assertTrue('Microsoft' in str(items[1].get('vendor')))
        self.assertTrue('Microsoft' in str(items[2].get('vendor')))
        self.assertTrue('Ubuntu' in str(items[3].get('vendor')))
        self.assertTrue(items[4].get('vendor') is None)

    def test_search_software_without_assigned_cpe_by_product_regex(self):
        software_1 = {'product': 'Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022'}
        software_2 = {'product': 'Internet Explorer'}
        software_3 = {'product': 'Microsoft Visual C++ 2013 Redistributable (x86) - 12.0.40649'}
        software_4 = {'product': 'Microsoft .NET Framework 4.6'}
        software_5 = {'product': 'Mozilla Firefox 48.0.2 (x86 en-GB)'}
        self.inventory_collection.insert_many(documents=[copy(software_1), copy(software_2), copy(software_3),
                                                         copy(software_4), copy(software_5)])
        sw_products = self.inventory.search_software_products_without_assigned_cpe('visuAL')
        self.assertEqual(2, len(sw_products))
        self.assertEqual(software_1, sw_products[0])
        self.assertEqual(software_3, sw_products[1])

        sw_products = self.inventory.search_software_products_without_assigned_cpe('')
        self.assertEqual(5, len(sw_products))

    def test_insert_new_software_products_to_db(self):
        item = copy(NEW_SOFTWARE_1)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        item = copy(NEW_SOFTWARE_2)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        item = copy(NEW_SOFTWARE_3)
        item.update({'id': self.generate_expected_software_id(item)})
        self.inventory_collection.insert_one(item)

        with patch('config.get_database_host', return_value=DB_HOST):
            with patch('config.get_database_port', return_value=DB_PORT):
                with patch('config.get_database_name', return_value=IVA_DB_NAME):
                    with patch('config.is_database_authentication_enabled', return_value=False):
                        with patch('inventory.glpi_inventory.read_inventory', return_value=GLPI_DB_ITEMS):
                            self.assertEqual(3, self.inventory_collection.count())
                            Inventory().insert_new_software_products_to_db()
                            self.assertEqual(5, self.inventory_collection.count())

    def test_get_software_product_from_inventory(self):
        software_id = 'a1f1h4j56'
        self.inventory_collection.insert_one(
            {'id': software_id, 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice',
             'vendor': 'Ubuntu', 'cpe': None, 'cve_matches': []})

        software = self.inventory.get_software_by_id(software_id)

        self.assertIsNotNone(software)
        self.assertEqual(software_id, software.get('id'))

    def test_get_vendors_returns_three_vendors(self):
        self.inventory_collection.insert_many(
            documents=[{'cpe': {'wfn': {'version': '0.6.15-2', 'product': 'accountsservice', 'vendor': 'ubuntu'}}},
                       {'cpe': {'wfn': {'version': '8', 'product': 'internet_explorer', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '1.3', 'product': 'iTunes', 'vendor': 'apple'}}}])

        vendors = self.inventory.get_vendors()
        self.assertEqual(3, len(vendors))
        self.assertTrue('ubuntu' in vendors)
        self.assertTrue('microsoft' in vendors)
        self.assertTrue('apple' in vendors)

    def test_get_vendors_returns_one_vendor(self):
        self.inventory_collection.insert_many(
            documents=[{'cpe': {'wfn': {'version': '9', 'product': 'internet_explorer', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '8', 'product': 'internet_explorer', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '7', 'product': 'internet_explorer', 'vendor': 'microsoft'}}}])
        vendors = self.inventory.get_vendors()
        self.assertEqual(1, len(vendors))
        self.assertTrue('microsoft' in vendors)

    def test_get_vendors_returns_empty_list(self):
        self.assertEqual(0, len(self.inventory.get_vendors()))

    def test_get_products_returns_three_products(self):
        self.inventory_collection.insert_many(
            documents=[{'cpe': {'wfn': {'version': '7', 'product': 'internet_explorer', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '8', 'product': 'office', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '2007', 'product': 'visual_c++', 'vendor': 'microsoft'}}}])
        products = self.inventory.get_products()
        self.assertEqual(3, len(products))
        self.assertTrue('internet_explorer' in products)
        self.assertTrue('office' in products)
        self.assertTrue('visual_c++' in products)

    def test_get_products_returns_one_product(self):
        self.inventory_collection.insert_many(
            documents=[{'cpe': {'wfn': {'version': '7', 'product': 'internet_explorer', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '10', 'product': 'internet_explorer', 'vendor': 'microsoft'}}}])
        products = self.inventory.get_products()
        self.assertEqual(1, len(products))
        self.assertTrue('internet_explorer' in products)

    def test_get_vendor_products(self):
        self.inventory_collection.insert_many(
            documents=[{'cpe': {'wfn': {'version': '0.6.15-2', 'product': 'accountsservice', 'vendor': 'ubuntu'}}},
                       {'cpe': {'wfn': {'version': '9', 'product': 'internet_explorer', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '8', 'product': 'office', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '7', 'product': 'office', 'vendor': 'microsoft'}}},
                       {'cpe': {'wfn': {'version': '1.3', 'product': 'iTunes', 'vendor': 'apple'}}}])

        products = self.inventory.get_vendor_products('microsoft')
        self.assertEqual(2, len(products))
        self.assertTrue('internet_explorer' in products)
        self.assertTrue('office' in products)

        products = self.inventory.get_vendor_products('ubuntu')
        self.assertEqual(1, len(products))
        self.assertTrue('accountsservice' in products)

        products = self.inventory.get_vendor_products('apple')
        self.assertEqual(1, len(products))
        self.assertTrue('iTunes' in products)

    def generate_expected_software_id(self, new_software):
        seed = str(new_software.get('product')) + str(new_software.get('vendor')) + str(new_software.get('version'))
        return hashlib.md5(str.encode(seed)).hexdigest()

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
