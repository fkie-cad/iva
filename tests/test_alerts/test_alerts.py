import unittest
import datetime
from pymongo import MongoClient
from unittest.mock import MagicMock
from alerts.alerts import ALERTS_DB_COLLECTION
from alerts.alert_sender import EmailSender
from inventory.inventory import INVENTORY_DB_COLLECTION
from tests.mock_config import *

SOFTWARE_ID = 'jdf5fh8qk5flo5a5'
CVE_ID = 'CVE-2012-5252'
DATE = datetime.datetime.now().isoformat()
NEW_ALERT_LOG_ENTRY = {'date':  DATE, 'event': 'new alert for' + CVE_ID}
ALERT = {'generated_on':  DATE, 'software_id': SOFTWARE_ID, 'cves': [CVE_ID], 'status': 'new',
         'log': [NEW_ALERT_LOG_ENTRY], 'notes': ''}


class TestAlerts(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.db = self.mongodb_client[IVA_DB_NAME]
        self.alerts_collection = self.db[ALERTS_DB_COLLECTION]
        self.inventory_collection = self.db[INVENTORY_DB_COLLECTION]
        self.create_alerts_object()

    def create_alerts_object(self):
        self.alerts = patch_config_for(module_name='alerts.alerts', class_name='Alerts')

    def test_insert_new_alert(self):
        self.insert_new_alert()

        # verify
        inserted_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertIsNotNone(inserted_alert)
        self.assertEqual(SOFTWARE_ID, inserted_alert.get('software_id'))
        cves = inserted_alert.get('cves')
        self.assertEqual(1, len(cves))
        self.assertEqual(CVE_ID, cves[0])
        self.assertEqual('new', inserted_alert.get('status'))
        self.assertEqual('', inserted_alert.get('notes'))
        self.verifyYYMMDD(inserted_alert.get('generated_on'))
        log = inserted_alert.get('log')
        self.assertEqual(1, len(log))
        self.assertEqual(NEW_ALERT_LOG_ENTRY.get('event'), log[0].get('event'))

    def insert_new_alert(self):
        with patch('alerts.alerts.generate_log_entry_for_new_alert') as alerts_logger_mock:
            alerts_logger_mock.return_value = NEW_ALERT_LOG_ENTRY
            self.alerts.insert_new_alert_for_inventory_item(SOFTWARE_ID, CVE_ID)

    def test_add_cve_to_alert(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one(ALERT)

        # insert new CVE
        new_cve = 'CVE-2016-1252'
        self.alerts.add_new_cve_to_alert(SOFTWARE_ID, new_cve)

        # verify
        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        cves = modified_alert.get('cves')
        self.assertEqual(2, len(cves))
        self.assertTrue(new_cve in cves)
        self.assertEqual(2, len(modified_alert.get('log')))

    def test_add_cve_to_alert_set_change_status_to_new_when_status_was_removed(self):
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [], 'status': 'removed', 'log': ['entry1', 'entry2'],
                                           'notes': ''})

        # add new CVE to alert
        with patch('alerts.alerts.generate_log_entry_for_changed_alert_status') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'changed to new'
            self.alerts.add_new_cve_to_alert(SOFTWARE_ID, 'cve1')

        # verify
        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertEqual('new', modified_alert.get('status'))

    def test_add_cve_to_alert_set_change_status_to_new_when_status_was_closed(self):
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [], 'status': 'closed', 'log': ['entry1', 'entry2'],
                                           'notes': ''})

        # add new CVE to alert
        with patch('alerts.alerts.generate_log_entry_for_changed_alert_status') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'changed to new'
            self.alerts.add_new_cve_to_alert(SOFTWARE_ID, 'cve1')

        # verify
        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertEqual('new', modified_alert.get('status'))
        self.assertTrue('changed to new' in modified_alert.get('log'))

    def test_remove_cve_from_alert(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': ['cve1', 'cve2'], 'status': 'new', 'log': [NEW_ALERT_LOG_ENTRY],
                                           'notes': ''})

        # remove cve from alert
        with patch('alerts.alerts.generate_log_entry_for_removed_cve') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'cve removed'
            self.alerts.remove_cve_from_alert(SOFTWARE_ID, 'cve1')

        # verify
        alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertEqual(1, len(alert.get('cves')))
        self.assertEqual('cve2', alert.get('cves')[0])
        self.assertEqual('new', alert.get('status'))
        log = alert.get('log')
        self.assertEqual(2, len(log))
        self.assertTrue('cve removed' in log)

    def test_remove_cve_from_alert_set_status_removed_when_last_cve_removed(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one(ALERT)

        # remove cve from alert
        with patch('alerts.alerts.generate_log_entry_for_changed_alert_status') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'status changed'
            self.alerts.remove_cve_from_alert(SOFTWARE_ID, CVE_ID)

        # verify
        alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertEqual(0, len(alert.get('cves')))
        self.assertEqual('removed', alert.get('status'))
        log = alert.get('log')
        self.assertEqual(3, len(log))
        self.assertTrue('status changed' in log)

    def test_change_status_new_to_closed(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one(ALERT)

        # change from new to closed
        with patch('alerts.alerts.generate_log_entry_for_changed_alert_status') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'status changed from new to closed'
            self.alerts.change_alert_status(SOFTWARE_ID, 'closed')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status was updated
        self.assertEqual('closed', modified_alert.get('status'))
        # verify status change was logged
        self.assertTrue('status changed from new to closed' in modified_alert.get('log'))
        # verify alert CVE were not modified
        self.assertEqual(1, len(modified_alert.get('cves')))
        self.assertEqual(CVE_ID, modified_alert.get('cves')[0])

    def test_change_status_new_to_removed(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one(ALERT)

        # change from new to removed
        with patch('alerts.alerts.generate_log_entry_for_changed_alert_status') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'status changed from new to removed'
            self.alerts.change_alert_status(SOFTWARE_ID, 'removed')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status was updated
        self.assertEqual('removed', modified_alert.get('status'))
        # verify status change was logged
        self.assertTrue('status changed from new to removed' in modified_alert.get('log'))
        # verify alert CVEs were removed
        self.assertEqual(0, len(modified_alert.get('cves')))

    def test_change_status_closed_to_new(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID, 'cves': [CVE_ID],
                                           'status': 'closed', 'log': ['entry1'], 'notes': ''})

        # change from closed to new
        with patch('alerts.alerts.generate_log_entry_for_changed_alert_status') as alerts_logger_mock:
            alerts_logger_mock.return_value = 'status changed from closed to new'
            self.alerts.change_alert_status(SOFTWARE_ID, 'new')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status was updated
        self.assertEqual('new', modified_alert.get('status'))
        # verify status change was logged
        self.assertTrue('status changed from closed to new' in modified_alert.get('log'))
        # verify alert CVEs not removed
        self.assertTrue(CVE_ID in modified_alert.get('cves'))

    def test_change_status_closed_to_new_not_possible_when_alerts_has_no_cve(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID, 'cves': [],
                                           'status': 'closed', 'log': ['entry1'], 'notes': ''})

        # change from closed to new'
        self.alerts.change_alert_status(SOFTWARE_ID, 'new')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status was still closed
        self.assertEqual('closed', modified_alert.get('status'))
        # verify no new log entry was added
        self.assertEqual(1, len(modified_alert.get('log')))
        # verify alert CVEs were not modified
        self.assertEqual(0, len(modified_alert.get('cves')))

    def test_change_status_closed_to_removed(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': ['cve1', 'cve2'], 'status': 'closed', 'log': ['entry1'], 'notes': ''})

        # change from closed to removed'
        self.alerts.change_alert_status(SOFTWARE_ID, 'removed')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status changed to removed
        self.assertEqual('removed', modified_alert.get('status'))
        # verify new log entry was added
        self.assertEqual(2, len(modified_alert.get('log')))
        # verify alert CVEs were removed
        self.assertEqual(0, len(modified_alert.get('cves')))

    def test_change_status_removed_to_new_is_not_possible(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [], 'status': 'removed', 'log': ['entry1'], 'notes': ''})

        # change from removed to new'
        self.alerts.change_alert_status(SOFTWARE_ID, 'new')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status was still removed
        self.assertEqual('removed', modified_alert.get('status'))
        # verify no new log entry was added
        self.assertEqual(1, len(modified_alert.get('log')))

    def test_change_status_removed_to_closed(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one({'generated_on': '', 'software_id': SOFTWARE_ID,
                                           'cves': [], 'status': 'removed', 'log': ['entry1'], 'notes': ''})

        # change from removed to closed'
        self.alerts.change_alert_status(SOFTWARE_ID, 'closed')

        modified_alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        # verify status changed to closed
        self.assertEqual('closed', modified_alert.get('status'))
        # verify new log entry was added
        self.assertEqual(2, len(modified_alert.get('log')))

    def test_update_alert_notes(self):
        # mock insert new alert for inventory item
        self.alerts_collection.insert_one(ALERT)

        # update notes
        self.alerts.update_notes(SOFTWARE_ID, 'new notes text')

        # verify
        alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
        self.assertEqual('new notes text', alert.get('notes'))

    def test_get_number_of_new_alerts_return_zero(self):
        self.assertEqual(0, self.alerts.get_number_of_new_alerts())

    def test_get_alerts_return_alerts_sorted_by_descending_date_and_status(self):
        # mock insert alerts
        alert_1_status_new = {'generated_on': '2016-11-02 12:06:32.992849', 'software_id': '1', 'cves': [],
                              'status': 'new', 'log': [], 'notes': ''}
        alert_2_status_new = {'generated_on': '2016-11-03 12:06:32.992849', 'software_id': '2', 'cves': [],
                              'status': 'new', 'log': [], 'notes': ''}
        alert_3_status_new = {'generated_on': '2016-11-03 13:06:32.992849', 'software_id': '3', 'cves': [],
                              'status': 'new', 'log': [], 'notes': ''}
        alert_1_status_closed = {'generated_on': '2016-08-03 13:06:32.992849', 'software_id': '4', 'cves': [],
                                 'status': 'closed', 'log': [], 'notes': ''}
        alert_2_status_closed = {'generated_on': '2016-10-25 13:06:32.992849', 'software_id': '5', 'cves': [],
                                 'status': 'closed', 'log': [], 'notes': ''}
        alert_1_status_removed = {'generated_on': '2015-07-03 13:06:32.992849', 'software_id': '6', 'cves': [],
                                  'status': 'removed', 'log': [], 'notes': ''}
        alert_2_status_removed = {'generated_on': '2016-07-03 13:06:32.992849', 'software_id': '7', 'cves': [],
                                  'status': 'removed', 'log': [], 'notes': ''}

        self.alerts_collection.insert_many(documents=[alert_3_status_new, alert_2_status_new, alert_1_status_new,
                                                      alert_2_status_closed, alert_1_status_closed,
                                                      alert_2_status_removed, alert_1_status_removed])

        # get alerts
        alerts = self.alerts.get_alerts()

        # verify
        self.assertEqual(7, len(alerts))
        self.assertEqual('1', alerts[0].get('software_id'))
        self.assertEqual('2', alerts[1].get('software_id'))
        self.assertEqual('3', alerts[2].get('software_id'))
        self.assertEqual('4', alerts[3].get('software_id'))
        self.assertEqual('5', alerts[4].get('software_id'))
        self.assertEqual('6', alerts[5].get('software_id'))
        self.assertEqual('7', alerts[6].get('software_id'))

    def test_send_alert_by_email(self):
        self.insert_software_to_db()
        self.alerts_collection.insert_one(ALERT)
        email_sender_mock = MagicMock(spec=EmailSender)
        email_sender_mock.send.return_value = True
        with patch('alerts.alerts.EmailSender', return_value=email_sender_mock):
            self.assertTrue(self.alerts.send_sw_alert_by_email(SOFTWARE_ID))
            email_sender_mock.send.assert_called_with(self.create_alert_for_email())
            alert = self.alerts_collection.find_one({'software_id': SOFTWARE_ID})
            self.assertEqual('sent', alert.get('status'))

    def test_send_alert_by_email_returns_false_when_email_sender_unable_to_send_email(self):
        self.insert_software_to_db()
        self.alerts_collection.insert_one(ALERT)
        email_sender_mock = MagicMock(spec=EmailSender)
        email_sender_mock.send.return_value = False
        with patch('alerts.alerts.EmailSender', return_value=email_sender_mock):
            self.assertFalse(self.alerts.send_sw_alert_by_email(SOFTWARE_ID))

    def insert_software_to_db(self):
        software = {'id': SOFTWARE_ID, 'version': '8', 'product': 'internet_explorer',
                    'vendor': 'microsoft', 'cpe': {'uri_binding': 'cpe:/a:microsoft:internet_explorer:8.0.7601.17514:::de',
                                                   'wfn': {}},
                    'cve_matches': [{'cve_id': CVE_ID, 'positive': 1, 'removed': 0, 'cpe_entries': []}]}
        self.inventory_collection.insert_one(software)

    def create_alert_for_email(self):
        alert = 'Generated on: ' + str(DATE) + '\n\nSoftware ID: '+SOFTWARE_ID+'\n\n' \
                'Product: internet_explorer\n\nVendor: microsoft\n\nVersion: 8\n\n' \
                'CPE: cpe:/a:microsoft:internet_explorer:8.0.7601.17514:::de\n\n' \
                'CVEs: '+str(ALERT.get('cves'))+'\n\nStatus: '+str(ALERT.get('status'))+'\n\n' \
                'Log:\n' + str(DATE) + ': new alert for' + CVE_ID + '\n\nNotes: '+str(ALERT.get('notes'))
        return alert

    def verifyYYMMDD(self, date):
        expected_yymmdd = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        self.assertRegex(str(date), expected_yymmdd, "Invalid Date")

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()


if __name__ == '__main__':
    unittest.main()
