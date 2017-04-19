import unittest
from unittest.mock import patch, MagicMock, Mock
from inventory import software_cpe
from django import template
from database import Database

template.loader = Mock(return_value='TemplateLoader')

GLPI_ITEM = {'id': 'dtr8ewg4af5dz9uj', 'os': '', 'vendor': 'microsoft_corporation',
             'product': 'microsoft_.net_framework_4_client_profile_deu_language_pack', 'version': '4.0.30319'}
WFN_POST = {'part': ['a'], 'vendor': ['microsoft'], 'product': ['.net_framework'], 'version': ['4.0.30319'],
            'update': ['ANY'], 'edition': ['ANY'], 'language': ['ANY'], 'sw_edition': ['ANY'], 'target_sw': ['ANY'],
            'target_hw': ['ANY'], 'other': ['ANY']}
WFN = {'part': 'a', 'vendor': 'microsoft', 'product': '.net_framework', 'version': '4.0.30319', 'update': 'ANY',
       'edition': 'ANY', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}
URI = 'cpe:/a:microsoft:.net_framework:4.0.30319'


class TestCaseAddCPEHandler(unittest.TestCase):

    def test_handle_post_request(self):
        cpe_inventory_mock = MagicMock(spec=software_cpe.SoftwareCPE)
        db_mock = MagicMock(spec=Database)
        with patch('django.http.HttpResponse', return_value=None):
            with patch('inventory.inventory.Database', return_value=db_mock):
                with patch('inventory.software_cpe.SoftwareCPE', return_value=cpe_inventory_mock):
                    from frontend.iva.handlers.assign_cpe_handler import handle_request
                    handle_request(MockPOSTRequest())
                    cpe_inventory_mock.create_sw_cpe_dict.assert_called_with(WFN)


class MockPOSTRequest:

    def __init__(self):
        self.method = 'POST'
        self.POST = create_post_dict()


def create_post_dict():
    dict_ = {'inventory_item': str(GLPI_ITEM), 'csrfmiddlewaretoken': ['G2Tg4v6Lo7pZ1bnIrz5b6X37jysLMTYH']}
    dict_.update(WFN_POST)
    return dict_


if __name__ == '__main__':
    unittest.main()