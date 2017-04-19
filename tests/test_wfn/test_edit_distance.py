import unittest
import editdistance
from matching.software_formatter import FormattedSoftware

class MyTestCase(unittest.TestCase):

    def test_something(self):
        software = {'vendor': 'Microsoft Corporation',
                    'product': 'Microsoft .NET Framework 4.5.2',
                    'version': '4.5.51209'}
        formatted_software = FormattedSoftware(software)
        # self.assertEqual(editdistance.eval('cpe:/a:microsoft:flash_player:9.0.115.0',
        #                                    'cpe:/a:micro:flash_player:9.0.115.0'), 1)


if __name__ == '__main__':
    unittest.main()
