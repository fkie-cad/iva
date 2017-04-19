import unittest
from tests.dict_tester import DictTester
from frontend.iva.handlers import request_handler_utils


class TestRequestHandlerUtils(unittest.TestCase):

    def setUp(self):
        self.dict_tester = DictTester()

    def test_is_post_request_returns_true(self):
        self.assertTrue(request_handler_utils.is_post_request(MockRequest('POST')))

    def test_is_post_request_returns_false(self):
        self.assertFalse(request_handler_utils.is_post_request(MockRequest('GET')))

    def test_is_get_request_returns_true(self):
        self.assertTrue(request_handler_utils.is_get_request(MockRequest('GET')))

    def test_is_get_request_returns_false(self):
        self.assertFalse(request_handler_utils.is_get_request(MockRequest('POST')))

    def test_is_post_request_returns_false_when_no_method(self):
        self.assertFalse(request_handler_utils.is_post_request(MockRequest('')))

    def test_is_get_request_returns_false_when_no_method(self):
        self.assertFalse(request_handler_utils.is_get_request(MockRequest('')))

    def test_create_dict_from_string(self):
        expected_dict = {'key': 'value1', 'key2': {'key3': 'value3'}}

        dict_string = '{"key": "value1", "key2": {"key3": "value3"}}'
        self.dict_tester.assertEqualKeys(expected_dict, request_handler_utils.create_dict_from_string(dict_string))
        self.dict_tester.assertEqualValues(expected_dict, request_handler_utils.create_dict_from_string(dict_string))

        dict_string = "{'key': 'value1', 'key2': {'key3': 'value3'}}"
        self.dict_tester.assertEqualKeys(expected_dict, request_handler_utils.create_dict_from_string(dict_string))
        self.dict_tester.assertEqualValues(expected_dict, request_handler_utils.create_dict_from_string(dict_string))

    def test_create_dict_from_string_returns_false(self):
        self.assertFalse(request_handler_utils.create_dict_from_string(''))
        self.assertFalse(request_handler_utils.create_dict_from_string(None))
        self.assertFalse(request_handler_utils.create_dict_from_string('[a, b, c]'))
        self.assertFalse(request_handler_utils.create_dict_from_string('{"a":}'))


class MockRequest:

    def __init__(self, method):
        self.method = method


if __name__ == '__main__':
    unittest.main()
