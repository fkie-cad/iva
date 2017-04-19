import unittest
from matching import software_formatter
from matching.software_formatter import FormattedSoftware

PROD_SEARCH_TERMS_NO_VER = ['microsoft', 'office', '201']
PROD_SEARCH_TERMS = ['microsoft', 'office', '2010']
UNFORMATTED_SW = {'product': 'Microsoft .NET Framework 4.5.2', 'vendor': 'Microsoft Corporation',
                  'version': '4.5.51209', 'os': 'Windows'}


class TestInventoryItem(unittest.TestCase):

    def setUp(self):
        self.formatted_software = FormattedSoftware(UNFORMATTED_SW)

    def test_get_product(self):
        self.assertEqual('microsoft_.net_framework_4.5.2', self.formatted_software.product)

    def test_get_vendor(self):
        self.assertEqual('microsoft_corporation', self.formatted_software.vendor)

    def test_get_os(self):
        self.assertEqual('Windows', self.formatted_software.os)

    def test_get_version(self):
        self.assertEqual('4.5.51209', self.formatted_software.get_version(PROD_SEARCH_TERMS))

    def test_get_version_when_sw_version_is_empty(self):
        formatted_sw = FormattedSoftware({'product': 'Microsoft Office 2010', 'vendor': 'Microsoft Corporation',
                                          'version': '', 'os': 'windows'})
        self.assertEqual('2010', formatted_sw.get_version(PROD_SEARCH_TERMS))

        formatted_sw = FormattedSoftware({'product': 'Microsoft Office 201', 'vendor': 'Microsoft Corporation',
                                          'version': '', 'os': 'windows'})
        self.assertEqual('', formatted_sw.get_version(PROD_SEARCH_TERMS_NO_VER))

    def test_format_product(self):
        sw_dict = {'product': 'FusionInventory Agent 2.3.17 (x86 edition)'}
        self.assertEqual('fusioninventory_agent_2.3.17_x86_edition', software_formatter.format_product(sw_dict))

    def test_format_vendor(self):
        sw_dict = {'vendor': 'Microsoft Corporation_'}
        self.assertEqual('microsoft_corporation', software_formatter.format_vendor(sw_dict))


if __name__ == '__main__':
    unittest.main()
