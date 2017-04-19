import unittest
from unittest.mock import MagicMock, patch, call

from alerts import alerts
from inventory import software_cve_matches

SOFTWARE_ID = 'd5f8sfd8sa4di90o'


class TestCaseChangeAlertStatusHandler(unittest.TestCase):

    def test_change_status_from_new_to_removed(self):
        # 1 Alerts: change status from new to remove
        # 2 CVE-Matches: set CVEs as negative
        alerts_mock = MagicMock(spec=alerts.Alerts)
        alerts_mock.get_software_alert.return_value = {'cves': ['cve1', 'cve2']}
        cve_matches_mock = MagicMock(spec=software_cve_matches.CVEMatches)
        with patch('django.http.HttpResponse', return_value=None):
            with patch('alerts.alerts.Alerts', return_value=alerts_mock):
                with patch('inventory.software_cve_matches.CVEMatches', return_value=cve_matches_mock):
                    from frontend.iva.handlers.alert_status_handler import handle_request
                    handle_request(MockPOSTRequest('removed'))
                    self.assertEqual(call.get_software_alert(SOFTWARE_ID), alerts_mock.method_calls[0])
                    self.assertEqual(call.change_alert_status(SOFTWARE_ID, 'removed'), alerts_mock.method_calls[1])
                    cve_matches_mock.set_cve_match_as_negative.assert_any_call(SOFTWARE_ID, 'cve1')
                    cve_matches_mock.set_cve_match_as_negative.assert_any_call(SOFTWARE_ID, 'cve2')

                    # only when status is set to removed CVEs are set as negative
                    handle_request(MockPOSTRequest('any_status'))
                    self.assertEqual(2, len(cve_matches_mock.method_calls))

                    handle_request(MockPOSTRequest('removed'))
                    self.assertEqual(4, len(cve_matches_mock.method_calls))


class MockPOSTRequest:

    def __init__(self, new_status):
        self.method = 'POST'
        self.POST = create_post_dict(new_status)


def create_post_dict(new_status):
    return {'software_id': SOFTWARE_ID, 'new_status': new_status}

if __name__ == '__main__':
    unittest.main()
