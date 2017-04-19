import re
import unittest

from matching.cpe_matcher_utils import create_regex, add_matches_to_list

special_chars = ['.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '\\', '|', '(', ')']
regex_start = '^'
regex_end = '.*'


class TestCPEMatcherUtils(unittest.TestCase):

    def test_create_regex_for_search_text_when_text_has_special_chars(self):
        for especial_char in special_chars:
            search_text = especial_char + 'search_text' + especial_char
            self.assertEqual(self.get_expected_regex(search_text), create_regex(search_text))

    def test_add_matches_to_list(self):
        matches = ['match_1', 'match_2', 'match_1', 'match_3']
        list_ = ['match_1', 'match_4']
        add_matches_to_list(matches, list_)
        self.assertEqual(4, len(list_))
        self.assertEqual('match_1', list_[0])
        self.assertEqual('match_2', list_[2])
        self.assertEqual('match_3', list_[3])
        self.assertEqual('match_4', list_[1])

    def test_add_matches_to_list_when_matches_list_empty(self):
        matches = []
        list_ = ['match_1', 'match_4']
        add_matches_to_list(matches, list_)
        self.assertEqual(2, len(list_))
        self.assertEqual('match_1', list_[0])
        self.assertEqual('match_4', list_[1])

    def get_expected_regex(self, search_text_with_special_chars):
        return regex_start + re.escape(search_text_with_special_chars) + regex_end


if __name__ == '__main__':
    unittest.main()
