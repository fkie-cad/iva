import unittest

from matching import search_terms_generator

vendor = 'microsoft_corporation_'


class TestSearchPhrasesGenerator(unittest.TestCase):

    def test_generate_search_phrases_for_product_returns_empty_list(self):
        product = ''
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 0)

    def test_generate_search_phrases_returns_one_phrase(self):
        product = 'product'
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 1)
        self.assertEqual(product, phrases[0])

    def test_generate_search_phrases_for_product_returns_three_phrases(self):
        product = 'first_second'
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 3)
        self.assertEqual('first_second', phrases[0])
        self.assertEqual('second', phrases[1])
        self.assertEqual('first', phrases[2])

    def test_generate_search_phrases_for_product_returns_five_phrases(self):
        product = 'first_second_third'
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 5)
        self.assertEqual('first_second_third', phrases[0])
        self.assertEqual('first_second', phrases[1])
        self.assertEqual('second', phrases[2])

    def test_generate_search_phrases_for_product_returns_seven_phrases(self):
        product = 'first_second_third_fourthfourthfourth'
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 7)
        self.assertEqual('first_second_third_fourthfourthfourth', phrases[0])
        self.assertEqual('first_second_third', phrases[1])
        self.assertEqual('first_second', phrases[2])
        self.assertEqual('fourthfourthfourth', phrases[3])
        self.assertEqual('second', phrases[4])
        self.assertEqual('third', phrases[5])
        self.assertEqual('first', phrases[6])

    def test_generate_search_phrases_for_product_does_not_excludes_vendor(self):
        product = 'first_second_third_microsoft'
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 7)
        self.assertTrue('first_second_third_microsoft' in phrases)
        self.assertTrue('microsoft' in phrases)

    def test_generate_search_phrases_for_product_excludes_phrases_smaller_than_three_chars(self):
        product = 'first_2_second_third_microsoft_lt_123'
        phrases = search_terms_generator.generate_product_search_terms(product, vendor)
        self.assertEqual(len(phrases), 13)
        self.assertFalse('lt' in phrases)
        self.assertFalse('2' in phrases)
        self.assertEqual('first_2_second_third_microsoft_lt_123', phrases[0])
        self.assertEqual('first_2_second_third_microsoft_lt', phrases[1])
        self.assertEqual('first_2_second_third_microsoft', phrases[2])
        self.assertEqual('first_2_second_third_lt_123', phrases[3])
        self.assertEqual('first_2_second_third_lt', phrases[4])
        self.assertEqual('first_2_second_third', phrases[5])
        self.assertEqual('first_2_second', phrases[6])
        self.assertEqual('first_2', phrases[7])
        self.assertEqual('microsoft', phrases[8])
        self.assertEqual('second', phrases[9])
        self.assertEqual('123', phrases[12])

    def test_remove_version_from_product_search_phrases(self):
        version = '4.5.2'
        search_phrases = ['.net_framework', version]
        search_phrases = search_terms_generator.remove_version_from_search_terms(search_phrases, version)
        self.assertEqual(len(search_phrases), 1)
        self.assertFalse(list(search_phrases).__contains__(version))

        search_phrases = ['.net_framework', '4.0']
        search_phrases = search_terms_generator.remove_version_from_search_terms(search_phrases, version)
        self.assertEqual(len(search_phrases), 2)
        self.assertTrue(list(search_phrases).__contains__('4.0'))

if __name__ == '__main__':
    unittest.main()
