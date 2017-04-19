import unittest
import datetime
from alerts import alerts_logger as logger

CVE = 'CVE-2016-0001'


class TestAlertsLogger(unittest.TestCase):

    def setUp(self):
        pass

    def test_log_new_alert(self):
        expected_log_entry = {'date': datetime.datetime.utcnow(), 'event': 'Alert generated due to ' + CVE}
        log_entry = logger.generate_log_entry_for_new_alert(CVE)
        self.verify(expected_log_entry, log_entry)

    def test_log_remove_cve(self):
        expected_log_entry = {'date': datetime.datetime.utcnow(), 'event': CVE + ' was removed'}
        log_entry = logger.generate_log_entry_for_removed_cve(CVE)
        self.verify(expected_log_entry, log_entry)

    def test_log_add_new_cve(self):
        expected_log_entry = {'date': datetime.datetime.utcnow(), 'event': CVE + ' was added'}
        log_entry = logger.generate_log_entry_for_added_cve(CVE)
        self.verify(expected_log_entry, log_entry)

    def test_log_change_alert_status(self):
        old_alert_status = 'new'
        new_alert_status = 'removed'
        expected_log_entry = {'date': datetime.datetime.utcnow(), 'event': 'Alert status changed: ' +
                                                                           old_alert_status + ' to ' + new_alert_status}
        log_entry = logger.generate_log_entry_for_changed_alert_status(old_alert_status, new_alert_status)
        self.verify(expected_log_entry, log_entry)

    def verify(self, expected_log_entry, log_entry):
        self.assertEqual(expected_log_entry.get('event'), log_entry.get('event'))
        self.verifyYYMMDD(log_entry.get('date'))

    def verifyYYMMDD(self, date):
        expected_yymmdd = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        self.assertRegex(str(date), expected_yymmdd, "Invalid Date")


if __name__ == '__main__':
    unittest.main()
