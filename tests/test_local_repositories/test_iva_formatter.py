import unittest
from tests.dict_tester import DictTester
from local_repositories import iva_formatter


CVE_ID = "CVE-1999-0004"
SUMMARY = "MIME buffer overflow in email clients, e.g. Solaris mailtool and Outlook."
VUL_CONFIG = ["cpe:2.3:a:hp:dtmail", "cpe:2.3:a:university_of_washington:pine:4.02", "cpe:2.3:o:sco:unixware:7.0"]
VUL_CONFIG_CPE_2_2 = ["cpe:/a:hp:dtmail", "cpe:/a:university_of_washington:pine:4.02", "cpe:/o:sco:unixware:7.0"]
CVE_SEARCH_CVE = {"id": CVE_ID, "summary": SUMMARY, "Modified": "2008-09-09T08:33:31.007Z",
                  "Published": "1997-12-16T00:00:00Z", "cvss": 5, "cvss-time": "2004-01-01T00:00:00Z",
                  "access": {"complexity": "LOW", "vector": "NETWORK", "authentication": "NONE"},
                  "references": ["http://www.microsoft.com/technet/security/bulletin/ms98-008.asp"],
                  "impact": {"availability": "PARTIAL", "integrity": "NONE", "confidentiality": "NONE"},
                  "vulnerable_configuration": VUL_CONFIG, "vulnerable_configuration_cpe_2_2": VUL_CONFIG_CPE_2_2}
CVE_KEYS = {'cve_id': '', 'cve_summary': '', 'cpe_entries': ''}
CVE_SEARCH_CPE = {"id": "cpe:2.3:a:%240.99_kindle_books_project:%240.99_kindle_books:6:-:-:-:-:android",
                  "references": ["https://play.google.com/store/apps/details?id=com.kindle.books.for99"],
                  "cpe_2_2": "cpe:/a:%240.99_kindle_books_project:%240.99_kindle_books:6::~~~android~~",
                  "title": "$0.99 Kindle Books project $0.99 Kindle Books (aka com.kindle.books.for99) for android 6.0"}
IVA_CPE = {"wfn": {"sw_edition": "ANY", "target_hw": "ANY", "version": "6", "target_sw": "android",
                   "vendor": "$0.99_kindle_books_project", "product": "$0.99_kindle_books", "edition": "ANY",
                   "language": "ANY", "part": "a", "update": "ANY", "other": "ANY"},
           "formatted_string_binding": "cpe:2.3:a:%240.99_kindle_books_project:%240.99_kindle_books:6:-:-:-:-:android",
           "uri_binding": "cpe:/a:%240.99_kindle_books_project:%240.99_kindle_books:6::~~~android~~"}

class TestIVAFormatter(unittest.TestCase):

    def setUp(self):
        self.dict_tester = DictTester()

    def test_format_cve(self):
        formatted_cve = iva_formatter.format_cve(CVE_SEARCH_CVE)
        self.dict_tester.assertEqualKeys(formatted_cve, CVE_KEYS)
        self.assertEqual(formatted_cve.get('cve_id'), CVE_ID)
        self.assertEqual(formatted_cve.get('cve_summary'), SUMMARY)
        self.verify_cpe_entries(formatted_cve)

    def verify_cpe_entries(self, formatted_cve):
        cpe_entries = formatted_cve.get('cpe_entries')
        self.assertEqual(len(cpe_entries), 3)
        self.verify_cpe_entry_has_correct_keys(cpe_entries)
        self.verify_uri_bindings(cpe_entries)

    def verify_cpe_entry_has_correct_keys(self, cpe_entries):
        self.dict_tester.assertEqualKeys(cpe_entries[0], {'uri_binding': '', 'wfn': ''})

    def get_uri_bindings(self, cpe_entries):
        uri_bindings = []
        for cpe in cpe_entries:
            uri_bindings.append(cpe.get('uri_binding'))
        return uri_bindings

    def verify_uri_bindings(self, cpe_entries):
        uri_bindings = self.get_uri_bindings(cpe_entries)
        for uri_binding in VUL_CONFIG_CPE_2_2:
            self.assertTrue(uri_binding in uri_bindings)

    def test_format_cpe(self):
        formatted_cpe = iva_formatter.format_cpe(CVE_SEARCH_CPE)
        self.dict_tester.assertEqualKeys(formatted_cpe, IVA_CPE)
        self.dict_tester.assertEqualValues(formatted_cpe, IVA_CPE)

if __name__ == '__main__':
    unittest.main()
