import unittest
from pymongo import MongoClient
from alerts.alerts import ALERTS_DB_COLLECTION
from inventory.inventory import INVENTORY_DB_COLLECTION
from inventory.software_cve_matches import sort_cve_matches_by_version
from tests.dict_tester import DictTester
from tests.mock_config import *

SOFTWARE_ID = '134jk429'


class TestCVEMatches(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.inventory_collection = self.test_db[INVENTORY_DB_COLLECTION]
        self.alerts_collection = self.test_db[ALERTS_DB_COLLECTION]
        self.dict_tester = DictTester()
        self.create_cve_matches_obj()

    def create_cve_matches_obj(self):
        self.cve_matches = patch_config_for('inventory.software_cve_matches', 'CVEMatches')

    def test_insert_matches(self):
        # insert software
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}}, 'cve_matches': []})

        # insert cve_matches for inventory item
        matches_found_for_software = [{'cve_id': 'CVE-2005-0509',
                                       'cve_summary': 'Multiple cross-site scripting (XSS) vulnerabilities',
                                       'cpe_entries': [{'uri_binding': 'cpe:/a:microsoft:.net_framework:1.0:sp2',
                                                        'wfn': {'language': 'ANY', 'version': '1.0',
                                                                'product': '.net_framework', 'edition': 'ANY',
                                                                'vendor': 'microsoft', 'other': 'ANY', 'update': 'sp2',
                                                                'part': 'a', 'sw_edition': 'ANY', 'target_sw': 'ANY',
                                                                'target_hw': 'ANY'}},
                                                       {'uri_binding': 'cpe:/a:microsoft:.net_framework:1.0',
                                                        'wfn': {'language': 'ANY', 'version': '1.0', 'product': '.net_framework',
                                                                'edition': 'ANY',
                                                                'vendor': 'microsoft', 'other': 'ANY', 'update': 'ANY',
                                                                'part': 'a', 'sw_edition': 'ANY', 'target_sw': 'ANY',
                                                                'target_hw': 'ANY'}}]},
                                      {'cve_id': 'CVE-2005-2127',
                                       'cve_summary': 'Microsoft Internet Explorer 5.01, 5.5, and 6 allows ."',
                                       'cpe_entries': [{'uri_binding': 'cpe:/a:microsoft:.net_framework:1.1',
                                                        'wfn': {'language': 'ANY', 'version': '1.1',
                                                                'product': '.net_framework', 'edition': 'ANY',
                                                                'vendor': 'microsoft', 'other': 'ANY',
                                                                'update': 'ANY', 'part': 'a', 'sw_edition': 'ANY',
                                                                'target_sw': 'ANY', 'target_hw': 'ANY'}}]}]
        self.cve_matches.insert_software_cve_matches(SOFTWARE_ID, matches_found_for_software)

        # verify that cve_matches for inventory item were inserted
        inserted_matches = self.inventory_collection.find_one({'id': SOFTWARE_ID}).get('cve_matches')
        self.assertIsNotNone(inserted_matches)
        # expected document must have two additional fields per match: positive and remove. Moreover, summary and
        # cpe_entries fields are deleted from each match
        expected_matches = [{'cve_id': 'CVE-2005-0509',
                             'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.0:sp2',
                                             'cpe:/a:microsoft:.net_framework:1.0'],
                             'positive': 0, 'removed': 0},
                            {'cve_id': 'CVE-2005-2127', 'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.1'],
                             'positive': 0, 'removed': 0}]
        self.assertListEqual(expected_matches, inserted_matches)

    def test_insert_matches_updates_matches_and_updates_alert_matches(self):
        # insert software with two matches
        cve_1 = {'cve_id': 'CVE-2005-0501', 'cpe_entries': [], 'positive': 1, 'removed': 0}
        cve_2 = {'cve_id': 'CVE-2005-0502', 'cpe_entries': [], 'positive': 0, 'removed': 0}
        cve_3 = {'cve_id': 'CVE-2005-0503', 'cpe_entries': [], 'positive': 1, 'removed': 0}
        self.inventory_collection.insert_one({'id': SOFTWARE_ID,
                                              'cve_matches': [cve_1, cve_2, cve_3],
                                              'cpe': {'uri_binding': 'cpe:/a:microsoft:.net_framework:1.1',
                                                      'wfn': {'version': '1.2'}}})

        # insert alert, since CVE-2005-0502 is positive
        self.alerts_collection.insert_one({'generated_on': '',
                                           'software_id': SOFTWARE_ID,
                                           'cves': ['CVE-2005-0501', 'CVE-2005-0503'], 'status': 'new',
                                           'log': [''], 'notes': ''})
        # insert new CVE matches
        # CVE already exist
        new_found_cve_1 = {'cve_id': 'CVE-2005-0501',
                           'cve_summary': 'Multiple cross-site scripting (XSS) vulnerabilities',
                           'cpe_entries': [{'uri_binding': 'cpe:/a:microsoft:.net_framework:1.0:sp2', 'wfn': ''},
                                           {'uri_binding': 'cpe:/a:microsoft:.net_framework:1.0', 'wfn': ''}]}
        # New CVE
        new_found_cve_4 = {'cve_id': 'CVE-2005-0504',
                           'cve_summary': 'Multiple cross-site scripting (XSS) vulnerabilities',
                           'cpe_entries': [{'uri_binding': 'cpe:/a:microsoft:.net_framework:1.0:sp2', 'wfn': ''},
                                           {'uri_binding': 'cpe:/a:microsoft:.net_framework:1.0', 'wfn': ''}]}
        cve_4 = {'cve_id': 'CVE-2005-0504', 'positive': 0, 'removed': 0,
                 'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.0:sp2', 'cpe:/a:microsoft:.net_framework:1.0']}

        self.cve_matches.insert_software_cve_matches(SOFTWARE_ID, [new_found_cve_1, new_found_cve_4])

        # verify that cve_matches for inventory item were updated
        updated_matches = self.inventory_collection.find_one({'id': SOFTWARE_ID}).get('cve_matches')
        self.assertEqual(2, len(updated_matches))
        self.assertTrue(cve_1 in updated_matches)
        self.assertTrue(cve_4 in updated_matches)

        # verify alert was updated
        alert_cves = self.alerts_collection.find_one({'software_id': SOFTWARE_ID}).get('cves')
        self.assertEqual(1, len(alert_cves))
        self.assertFalse('CVE-2005-0503' in alert_cves)
        self.assertTrue('CVE-2005-0501' in alert_cves)

    def test_add_new_match(self):
        # insert software
        software_matches = [{'cve_id': 'CVE-2005-0509', 'cpe_entries': ['cpe:/a:microsoft:.net_framework:3.5'],
                             'positive': 0, 'removed': 1}]
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                                              'cve_matches': software_matches})

        # add new match to software
        new_match = {'cve_id': 'CVE-2016-0149', 'cve_summary': 'Microsoft .NET Framework 2.0, 3.0 SP2, 3.5, 3.5.1,"',
                     'cpe_entries': [{'uri_binding': 'cpe:/a:microsoft:.net_framework:3.5.1',
                                      'wfn': {'language': 'ANY', 'version': '3.5.1', 'product': '.net_framework',
                                              'edition': 'ANY', 'vendor': 'microsoft', 'other': 'ANY', 'update': 'ANY',
                                              'part': 'a', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY'}}]}
        self.cve_matches.add_new_cve_match_to_software(SOFTWARE_ID, new_match)

        # verify
        expected_matches = [{'cve_id': 'CVE-2005-0509', 'positive': 0, 'removed': 1,
                             'cpe_entries': ['cpe:/a:microsoft:.net_framework:3.5']},
                            {'cve_id': 'CVE-2016-0149', 'positive': 0, 'removed': 0,
                             'cpe_entries': ['cpe:/a:microsoft:.net_framework:3.5.1']}]
        updated_matches = self.inventory_collection.find_one({'id': SOFTWARE_ID}).get('cve_matches')
        self.assertListEqual(expected_matches, updated_matches)

    def test_set_match_as_removed(self):
        # insert document to be updated
        cve_id = 'CVE-2005-0509'
        software = {'id': SOFTWARE_ID,
                    'cve_matches': [{'cve_id': cve_id, 'positive': 0, 'removed': 0, 'cpe_entries': []}],
                    'cpe': {'wfn': {'version': '1.2'}}}
        self.inventory_collection.insert_one(software)

        self.cve_matches.set_cve_match_as_removed(SOFTWARE_ID, cve_id)

        # self.verify_cve_match_status('removed', 1)
        match = self.get_software_cve_match(SOFTWARE_ID, cve_id)
        self.assertEqual(1, match.get('removed'))

    def test_restore_cve_match(self):
        # insert document to be updated
        cve_id = 'CVE-2005-0509'
        software = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': cve_id, 'positive': 0, 'removed': 1, 'cpe_entries': []}]}
        self.inventory_collection.insert_one(software)

        self.cve_matches.restore_cve_match(SOFTWARE_ID, cve_id)

        match = self.get_software_cve_match(SOFTWARE_ID, cve_id)
        self.assertEqual(0, match.get('removed'))

    def test_set_match_as_positive(self):
        # insert document to be updated
        cve_id = 'CVE-2005-0509'
        software = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': cve_id, 'positive': 0, 'removed': 0, 'cpe_entries': []}]}
        self.inventory_collection.insert_one(software)

        # set cve match as positive
        self.cve_matches.set_cve_match_as_positive(SOFTWARE_ID, cve_id)

        # verify status was changed to positive
        match = self.get_software_cve_match(SOFTWARE_ID, cve_id)
        self.assertEqual(1, match.get('positive'))

        # verify new alert was generated
        self.assertIsNotNone(self.alerts_collection.find_one({'software_id': SOFTWARE_ID}))

    def test_set_match_as_positive_does_not_create_new_alert_when_already_alert_exists(self):
        cve_id = 'CVE-2005-0509'
        software = {'id': SOFTWARE_ID,
                    'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': cve_id, 'positive': 0, 'removed': 0, 'cpe_entries': []}]}
        self.inventory_collection.insert_one(software)

        self.assertEqual(0, len(list(self.alerts_collection.find({'software_id': SOFTWARE_ID}))))
        # when the first CVE is set as positive an alert is created. For the next ones, the created alert is updated
        self.cve_matches.set_cve_match_as_positive(SOFTWARE_ID, cve_id)
        self.cve_matches.set_cve_match_as_positive(SOFTWARE_ID, cve_id)
        self.assertEqual(1, len(list(self.alerts_collection.find({'software_id': SOFTWARE_ID}))))

    def test_set_match_as_negative(self):
        # insert document to be updated
        cve_id = 'CVE-2005-0509'
        software = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': cve_id, 'positive': 1, 'removed': 1, 'cpe_entries': []}], }
        self.inventory_collection.insert_one(software)

        self.alerts_collection.insert_one({'generated_on': '',
                                           'software_id': SOFTWARE_ID,
                                           'cves': [cve_id, 'CVE-2005-0510'], 'status': 'new',
                                           'log': [''], 'notes': ''})

        # set cve as negative
        self.cve_matches.set_cve_match_as_negative(SOFTWARE_ID, cve_id)

        # verify status changed to negative
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id).get('positive'))

        # verify CVE-2005-0509 was removed from item alert
        alert_cves = self.alerts_collection.find_one({'software_id': SOFTWARE_ID}).get('cves')
        self.assertTrue(cve_id not in alert_cves)

    def test_exist_cve_matches_for_software_returns_true(self):
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                                              'cve_matches': [{'cve_id': 'CVE-2005-0509', 'positive': 1, 'removed': 1,
                                                               'cpe_entries': []}]})
        self.assertTrue(self.cve_matches.exist_cve_matches_for_software(SOFTWARE_ID))

    def test_exist_cve_matches_for_inventory_item_return_false(self):
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'cve_matches': [], 'cpe': {'wfn': {'version': '1.2'}}})
        self.assertFalse(self.cve_matches.exist_cve_matches_for_software(SOFTWARE_ID))

    def test_get_software_cve_matches_returns_one_match(self):
        # insert software with one CVE match
        self.inventory_collection.insert_one({'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                                              'cve_matches': [{'cve_id': 'CVE-2005-0509', 'positive': 1, 'removed': 1,
                                                               'cpe_entries': []}]})
        # verify
        self.assertEqual(1, len(self.cve_matches.get_software_cve_matches(SOFTWARE_ID)))

    def test_get_all_vulnerable_software_returns_two_items(self):
        vulnerable_software_1 = {'id': '1478', 'cpe': {'wfn': {'version': '1.2'}},
                                 'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 0, 'positive': 1,
                                                  'cve_summary': '', 'cpe_entries': []},
                                                 {'cve_id': 'CVE-2005-0510', 'removed': 1, 'positive': 0,
                                                  'cve_summary': '', 'cpe_entries': []}]}

        not_vulnerable_software = {'id': '68665', 'cpe': {'wfn': {'version': '1.2'}},
                                   'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 0, 'positive': 0,
                                                    'cve_summary': '', 'cpe_entries': []},
                                                   {'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 0,
                                                    'cve_summary': '', 'cpe_entries': []}]}

        vulnerable_software_2 = {'id': '45469', 'cpe': {'wfn': {'version': '1.2'}},
                                 'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 1, 'positive': 0,
                                                  'cve_summary': '', 'cpe_entries': []},
                                                 {'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 1,
                                                  'cve_summary': '', 'cpe_entries': []}]}

        self.inventory_collection.insert_many(documents=[vulnerable_software_1, vulnerable_software_2, not_vulnerable_software])

        # verify
        vulnerable_software_items = self.cve_matches.get_vulnerable_software_items()
        self.assertEqual(2, len(vulnerable_software_items))
        self.assertEqual('1478', vulnerable_software_items[0].get('id'))
        self.assertEqual('45469', vulnerable_software_items[1].get('id'))

    def test_get_software_cve_matches_for_returns_three_matches(self):
        # insert software with 3 CVE matches
        software = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 0, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []},
                                    {'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []},
                                    {'cve_id': 'CVE-2005-0510', 'removed': 1, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []}]}

        self.inventory_collection.insert_one(software)

        # verify
        self.assertEqual(3, len(self.cve_matches.get_software_cve_matches(SOFTWARE_ID)))

    def test_get_software_cve_matches_returns_two_matches(self):
        # insert software with 2 matches
        software = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 1, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []},
                                    {'cve_id': 'CVE-2005-0510', 'removed': 1, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []}]}
        self.inventory_collection.insert_one(software)

        # verify
        self.assertEqual(2, len(self.cve_matches.get_software_cve_matches(SOFTWARE_ID)))

    def test_remove_software_cve_matches(self):
        # insert software with CVE matches to be deleted
        software = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                    'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 1, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []},
                                    {'cve_id': 'CVE-2005-0510', 'removed': 1, 'positive': 0,
                                     'cve_summary': '', 'cpe_entries': []}]}
        self.inventory_collection.insert_one(software)

        # remove software CVE matches
        self.cve_matches.remove_software_cve_matches(SOFTWARE_ID)

        # verify
        software = self.inventory_collection.find_one({'id': SOFTWARE_ID})
        self.assertEqual(0, len(software.get('cve_matches')))

    def test_get_cve_matches_returns_one_match(self):
        # insert software items
        software_1 = {'id': SOFTWARE_ID, 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice',
                      'vendor': 'Ubuntu', 'cpe': {'wfn': {'version': '1.2'}},
                      'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 0, 'positive': 0, 'cpe_entries': []}]}
        software_2 = {'id': '123', 'cpe': {'wfn': {'version': '1.2'}}, 'cve_matches': []}
        software_3 = {'id': '124', 'cpe': {'wfn': {'version': '1.2'}}, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get software with CVE matches
        cve_matches = self.cve_matches.get_cve_matches()

        # verify
        expected_match = {'cve_id': 'CVE-2005-0509', 'removed': 0, 'positive': 0, 'cpe_entries': [],
                          'software': {'id': SOFTWARE_ID, 'version': '0.6.15-2ubuntu9.7', 'product': 'accountsservice',
                                       'vendor': 'Ubuntu', 'cpe': {'wfn': {'version': '1.2'}}}}
        self.assertEqual(1, len(cve_matches))
        self.dict_tester.assertEqualKeys(expected_match, cve_matches[0])
        self.dict_tester.assertEqualValues(expected_match, cve_matches[0])

    def test_get_cve_matches_returns_empty_list(self):
        self.assertEqual(0, len(self.cve_matches.get_cve_matches()))

    def test_get_software_items_with_cve_matches_returns_three_matches(self):
        # insert software items
        software_1 = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                      'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 0, 'positive': 0, 'cve_summary': '',
                                       'cpe_entries': []}]}
        software_2 = {'id': '123', 'cpe': {'wfn': {'version': '1.2'}},
                      'cve_matches': [{'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 0, 'cve_summary': '',
                                       'cpe_entries': []}, {'cve_id': 'CVE-2005-0511', 'removed': 0, 'positive': 0,
                                                            'cve_summary': '', 'cpe_entries': []}]}
        software_3 = {'id': '124', 'cpe': {'wfn': {'version': '1.2'}}, 'cve_matches': []}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get software with CVE matches
        cve_matches = self.cve_matches.get_cve_matches()

        # verify
        self.assertEqual(3, len(cve_matches))

    def test_get_cve_matches_without_removed_matches(self):
        # insert software items
        software_1 = {'id': SOFTWARE_ID, 'cpe': {'wfn': {'version': '1.2'}},
                      'cve_matches': [{'cve_id': 'CVE-2005-0509', 'removed': 1, 'positive': 0, 'cve_summary': '',
                                       'cpe_entries': []}, {'cve_id': 'CVE-2005-0510', 'removed': 1, 'positive': 0,
                                                            'cve_summary': '', 'cpe_entries': []}]}
        software_2 = {'id': '123', 'cve_matches': [], 'cpe': {'wfn': {'version': '1.2'}}}
        software_3 = {'id': '124', 'cve_matches': [{'cve_id': 'CVE-2005-0511', 'removed': 0, 'positive': 0,
                                                    'cve_summary': '', 'cpe_entries': []}], 'cpe': {'wfn': {'version': '1.2'}}}
        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get software with CVE matches
        software_with_cve_matches = self.cve_matches.get_cve_matches(['hide_removed'])

        # verify
        self.assertEqual(1, len(software_with_cve_matches))
        self.assertEqual('CVE-2005-0511', software_with_cve_matches[0].get('cve_id'))
        self.assertEqual('124', software_with_cve_matches[0].get('software').get('id'))

    def test_get_cve_matches_ordered_by_cve_year_descending(self):
        # insert software items
        software_1 = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 0,
                                                          'cpe_entries': []},
                                                         {'cve_id': 'CVE-2005-0519', 'removed': 1, 'positive': 0,
                                                          'cpe_entries': []}]}
        software_2 = {'id': '123', 'cve_matches': [{'cve_id': 'CVE-2005-0501', 'removed': 1, 'positive': 0,
                                                    'cpe_entries': []},
                                                   {'cve_id': 'CVE-2016-9999', 'removed': 1, 'positive': 0,
                                                    'cpe_entries': []}]}

        self.inventory_collection.insert_many(documents=[software_1, software_2])

        # get software with CVE matches
        cve_matches = self.cve_matches.get_cve_matches(['ordered_by_year_desc'])

        # verify
        self.assertEqual(cve_matches[0].get('cve_id'), 'CVE-2016-9999')
        self.assertEqual(cve_matches[1].get('cve_id'), 'CVE-2005-0519')
        self.assertEqual(cve_matches[2].get('cve_id'), 'CVE-2005-0510')
        self.assertEqual(cve_matches[3].get('cve_id'), 'CVE-2005-0501')

    def test_get_cve_matches_ordered_by_cve_year_ascending(self):
        # insert software items
        software_1 = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 0,
                                                          'cpe_entries': []},
                                                         {'cve_id': 'CVE-2005-0519', 'removed': 1, 'positive': 0,
                                                          'cpe_entries': []}]}
        software_2 = {'id': '123', 'cve_matches': [{'cve_id': 'CVE-2004-0501', 'removed': 1, 'positive': 0,
                                                    'cpe_entries': []},
                                                   {'cve_id': 'CVE-2016-9999', 'removed': 1, 'positive': 0,
                                                    'cpe_entries': []}]}

        self.inventory_collection.insert_many(documents=[software_1, software_2])

        # get software with CVE matches
        cve_matches = self.cve_matches.get_cve_matches(['ordered_by_year_asc'])

        # verify
        self.assertEqual(cve_matches[0].get('cve_id'), 'CVE-2004-0501')
        self.assertEqual(cve_matches[1].get('cve_id'), 'CVE-2005-0510')
        self.assertEqual(cve_matches[2].get('cve_id'), 'CVE-2005-0519')
        self.assertEqual(cve_matches[3].get('cve_id'), 'CVE-2016-9999')

    def test_get_cve_matches_without_cve_matches_ordered_by_cve(self):
        # insert software items
        software_1 = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': 'CVE-2005-0510', 'removed': 0, 'positive': 0,
                                                          'cpe_entries': []},
                                                         {'cve_id': 'CVE-2005-0501', 'removed': 1, 'positive': 0,
                                                          'cpe_entries': []}]}
        software_2 = {'id': '123', 'cve_matches': [{'cve_id': 'CVE-2005-0519', 'removed': 1, 'positive': 0,
                                                    'cpe_entries': []}]}
        software_3 = {'id': '124', 'cve_matches': [{'cve_id': 'CVE-2006-9999', 'removed': 0, 'positive': 0,
                                                    'cpe_entries': []}]}

        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        # get software with CVE matches
        cve_matches = self.cve_matches.get_cve_matches(['ordered_by_year_desc', 'hide_removed'])

        # verify
        self.assertEqual(2, len(cve_matches))
        self.assertEqual(cve_matches[0].get('cve_id'), 'CVE-2006-9999')
        self.assertEqual(cve_matches[1].get('cve_id'), 'CVE-2005-0510')
        self.assertEqual(cve_matches[0].get('software').get('id'), '124')
        self.assertEqual(cve_matches[1].get('software').get('id'), SOFTWARE_ID)

    def test_get_vendor_product_cves_matches(self):
        # insert software items
        matches_1 = [{'cve_id': 'CVE-2005-0509'}, {'cve_id': 'CVE-2005-2127'}]
        matches_2 = [{'cve_id': 'CVE-2005-0510'}, {'cve_id': 'CVE-2005-2128'}]
        matches_3 = [{'cve_id': 'CVE-2005-0511'}, {'cve_id': 'CVE-2005-2129'}]
        software_1 = {'cpe': {'wfn': {'vendor': 'microsoft', 'product': 'office'}}, 'cve_matches': matches_1}
        software_2 = {'cpe': {'wfn': {'vendor': 'microsoft', 'product': 'internet_explorer'}}, 'cve_matches': matches_2}
        software_3 = {'cpe': {'wfn': {'vendor': 'ubuntu', 'product': 'openssl'}}, 'cve_matches': matches_3}

        self.inventory_collection.insert_many(documents=[software_1, software_2, software_3])

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('all')
        self.assertEqual(6, len(cve_matches))

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('microsoft')
        self.assertEqual(4, len(cve_matches))

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('ubuntu')
        self.assertEqual(2, len(cve_matches))

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('microsoft', 'office')
        self.assertEqual(2, len(cve_matches))

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('microsoft', 'internet_explorer')
        self.assertEqual(2, len(cve_matches))

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('microsoft', 'visual_studio')
        self.assertEqual(0, len(cve_matches))

        cve_matches = self.cve_matches.get_vendor_product_cve_matches('apple', 'itunes')
        self.assertEqual(0, len(cve_matches))

    def test_get_software_cve_matches_with_same_cpe_entries_as_cve(self):
        cve_id = 'CVE-2005-0510'
        cpe_entries = ['cpe:/a:microsoft:.net_framework:1.0:sp2']
        software = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': cve_id, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': 'CVE-2005-0501', 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': 'CVE-2002-0089', 'removed': 0, 'positive': 0,
                                                        'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.0:sp2',
                                                                        'cpe:/a:microsoft:.net_framework:1.0:sp1']},
                                                       {'cve_id': 'CVE-2016-0001', 'removed': 0, 'positive': 0,
                                                        'cpe_entries': ['cpe:/a:microsoft:.net_framework:4.0:sp2']}],
                    'cpe': {'wfn': {'version': '1.8'}}}
        self.inventory_collection.insert_one(software)
        cve_matches = self.cve_matches.get_software_cve_matches_with_same_cpe_entries_as_cve(SOFTWARE_ID, cve_id)
        self.assertEqual(2, len(cve_matches))
        self.assertEqual(cve_id, cve_matches[0].get('cve_id'))
        self.assertEqual('CVE-2005-0501', cve_matches[1].get('cve_id'))

    def test_get_software_cve_matches_with_same_cpe_entries_removed_and_positive_values_as_cve(self):
        cve_id = 'CVE-2005-0510'
        cpe_entries = ['cpe:/a:microsoft:.net_framework:1.0:sp2']
        software = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': cve_id, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': 'CVE-2005-0501', 'removed': 0, 'positive': 1,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': 'CVE-2006-9928', 'removed': 1, 'positive': 0,
                                                        'cpe_entries': cpe_entries}], 'cpe': {'wfn': {'version': '1.2'}}}
        self.inventory_collection.insert_one(software)
        cve_matches = self.cve_matches.get_software_cve_matches_with_same_cpe_entries_as_cve(SOFTWARE_ID, cve_id)
        self.assertEqual(1, len(cve_matches))
        self.assertEqual(cve_id, cve_matches[0].get('cve_id'))

    def test_set_matches_group_as_positive(self):
        cve_id_master = 'CVE-2005-0510'
        cve_id_1 = 'CVE-2005-0501'
        cve_id_2 = 'CVE-2006-9928'
        cpe_entries = ['cpe:/a:microsoft:.net_framework:1.0:sp2']
        software = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': cve_id_master, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_1, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_2, 'removed': 1, 'positive': 0,
                                                        'cpe_entries': cpe_entries}], 'cpe': {'wfn': {'version': '1.2'}}}
        self.inventory_collection.insert_one(software)
        self.cve_matches.set_cve_matches_group_as_positive(SOFTWARE_ID, cve_id_master)
        self.assertEqual(1, self.get_software_cve_match(SOFTWARE_ID, cve_id_master).get('positive'))
        self.assertEqual(1, self.get_software_cve_match(SOFTWARE_ID, cve_id_1).get('positive'))
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_2).get('positive'))

    def test_set_matches_group_as_negative(self):
        cve_id_master = 'CVE-2005-0510'
        cve_id_1 = 'CVE-2005-0501'
        cve_id_2 = 'CVE-2006-9928'
        cpe_entries = ['cpe:/a:microsoft:.net_framework:1.0:sp2']
        software = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': cve_id_master, 'removed': 0, 'positive': 1,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_1, 'removed': 0, 'positive': 1,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_2, 'removed': 1, 'positive': 0,
                                                        'cpe_entries': cpe_entries}], 'cpe': {'wfn': {'version': '1.2'}}}
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [cve_id_master, cve_id_1, cve_id_2],
                                           'status': 'new', 'log': [''], 'notes': ''})
        self.inventory_collection.insert_one(software)
        self.cve_matches.set_cve_matches_group_as_negative(SOFTWARE_ID, cve_id_master)
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_master).get('positive'))
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_1).get('positive'))
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_2).get('positive'))

    def test_set_cve_matches_group_as_removed(self):
        cve_id_master = 'CVE-2005-0510'
        cve_id_1 = 'CVE-2005-0501'
        cve_id_2 = 'CVE-2006-9928'
        cpe_entries = ['cpe:/a:microsoft:.net_framework:1.0:sp2']
        software = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': cve_id_master, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_1, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_2, 'removed': 0, 'positive': 1,
                                                        'cpe_entries': cpe_entries}],
                    'cpe': {'wfn': {'version': '1.2'}}}
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [cve_id_master, cve_id_1, cve_id_2],
                                           'status': 'new', 'log': [''], 'notes': ''})
        self.inventory_collection.insert_one(software)
        self.cve_matches.set_cve_matches_group_as_removed(SOFTWARE_ID, cve_id_master)
        self.assertEqual(1, self.get_software_cve_match(SOFTWARE_ID, cve_id_master).get('removed'))
        self.assertEqual(1, self.get_software_cve_match(SOFTWARE_ID, cve_id_1).get('removed'))
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_2).get('removed'))

    def test_restore_cve_matches_group(self):
        cve_id_master = 'CVE-2005-0510'
        cve_id_1 = 'CVE-2005-0501'
        cve_id_2 = 'CVE-2006-9928'
        cpe_entries = ['cpe:/a:microsoft:.net_framework:1.0:sp2']
        software = {'id': SOFTWARE_ID, 'cve_matches': [{'cve_id': cve_id_master, 'removed': 1, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_1, 'removed': 1, 'positive': 0,
                                                        'cpe_entries': cpe_entries},
                                                       {'cve_id': cve_id_2, 'removed': 0, 'positive': 0,
                                                        'cpe_entries': cpe_entries}],'cpe': {'wfn': {'version': '1.2'}}}
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [cve_id_master, cve_id_1, cve_id_2],
                                           'status': 'new', 'log': [''], 'notes': ''})
        self.inventory_collection.insert_one(software)
        self.cve_matches.restore_cve_matches_group(SOFTWARE_ID, cve_id_master)
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_master).get('removed'))
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_1).get('removed'))
        self.assertEqual(0, self.get_software_cve_match(SOFTWARE_ID, cve_id_2).get('removed'))

    def test_cve_matches_are_prioritized_by_equal_version(self):
        software = {'id': SOFTWARE_ID, 'cve_matches': [], 'cpe': {'wfn': {'version': '1.5.6'}}}
        matches = [{'cve_id': 'CVE-2015-0001', 'removed': 1, 'positive': 0,
                    'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.0:sp2',
                                    'cpe:/a:microsoft:.net_framework:1.2.0:sp2']},
                   {'cve_id': 'CVE-2015-0002', 'removed': 1, 'positive': 0,
                    'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.6',
                                    'cpe:/a:microsoft:.net_framework:1.9:sp2']},
                   {'cve_id': 'CVE-2015-0003', 'removed': 0, 'positive': 0,
                    'cpe_entries': ['cpe:/a:microsoft:.net_framework:1.0:sp2',
                                    'cpe:/a:microsoft:.net_framework:1.5.6:sp2']}]
        self.inventory_collection.insert_one(software)
        sorted_matches = sort_cve_matches_by_version(matches, '1.5.6')
        self.assertEqual('CVE-2015-0003', sorted_matches[0].get('cve_id'))

    def get_software_cve_match(self, software_id, cve_id):
        matches = self.inventory_collection.find_one({'id': software_id}).get('cve_matches')
        for match in matches:
            if match.get('cve_id') == cve_id:
                return match

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
