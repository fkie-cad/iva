import unittest

from wfn.encoding import Decoder


class TestDecoder(unittest.TestCase):

    def test_decode_non_alphanumeric_characters(self):
        # {'%21': '!', '%22': '\"', '%23': '#', '%24': '$', '%25': '%', '%26': '&', '%27': '\'',
        # '%28': '(', '%29': ')', '%2a': '*',  '%2b': '+', '%2c': ',',
        # '%2f': '/', '%3a': ':', '%3b': ';',  '%3c': '<', '%3d': '=', '%3e': '>', '%3f': '?',
        # '%40': '@', '%5b': '[', '%5c': '\\', '%5d': ']', '%5e': '^', '%60': '`', '%7b': '{',
        # '%7c': '|', '%7d': '}',  '%7e': '~',
        # '%01': '?', '%02': '*'}
        self.assertEqual('text!1text%!text', Decoder.decode_non_alphanumeric_characters('text%211text%25%21text'))
        self.assertEqual('text!1text%!text\"text\"2text%\"text', Decoder.decode_non_alphanumeric_characters('text%211text%25%21text%22text%222text%25%22text'))
        self.assertEqual('\"text\"2text%\"text]text]d_text%]]text', Decoder.decode_non_alphanumeric_characters('%22text%222text%25%22text%5dtext%5dd_text%25%5d%5dtext'))
        self.assertEqual('\"text\"2text%\"text]text]d_text%]]text~e~text~e~', Decoder.decode_non_alphanumeric_characters('%22text%222text%25%22text%5dtext%5dd_text%25%5d%5dtext%7ee%7etext%7ee%7e'))

if __name__ == '__main__':
    unittest.main()
