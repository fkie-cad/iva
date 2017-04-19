import unittest
from tests.dict_tester import DictTester
from wfn.wfn_converter import WFNConverter


class TestWFNConverter(unittest.TestCase):

    def setUp(self):
        self.test_utils = DictTester()
        self.wfn_converter = WFNConverter()

    def test_converter_cpe_uri_to_wfn(self):
        # taken from CPE-Naming.pdf
        # Example 1
        # cpe:/a:microsoft:internet_explorer:8.0.6001:beta
        # wfn:[part="a",vendor="microsoft",product="internet_explorer", version="8\.0\.6001",update="beta",edition=ANY, language=ANY]

        cpe_uri = 'cpe:/a:microsoft:internet_explorer:8.0.6001:beta'

        expected_wfn_document = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer',
                                 'version': '8.0.6001', 'update': 'beta', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # normally, double points (:) are encoded to (%3a). However, if for some reason the encoding was not performed
        # during the creation of the CPE URI, we have to consider this case and create the corresponding WFN correctly.
        cpe_uri = 'cpe:/a:string_value_with\:double_points:internet_explorer:8.0.6001:beta'
        expected_wfn_document = {'part': 'a', 'vendor': 'string_value_with:double_points', 'product': 'internet_explorer',
                                 'version': '8.0.6001', 'update': 'beta', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 2
        # cpe:/a:microsoft:internet_explorer:8.%2a:sp%3f
        # wfn:[part="a",vendor="microsoft",product="internet_explorer", version="8\.\*",update="sp\?",edition=ANY,language=ANY]
        cpe_uri = 'cpe:/a:microsoft:internet_explorer:8.%2a:sp%3f'
        expected_wfn_document = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer',
                                 'version': '8.*', 'update': 'sp?', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 3
        # cpe:/a:microsoft:internet_explorer:8.%02:sp%01
        # wfn:[part="a",vendor="microsoft",product="internet_explorer", version="8\.*",update="sp?",edition=ANY,language=ANY]
        cpe_uri = 'cpe:/a:microsoft:internet_explorer:8.%02:sp%01'
        expected_wfn_document = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer',
                                 'version': '8.*', 'update': 'sp?', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY',	'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 4
        # cpe:/a:hp:insight_diagnostics:7.4.0.1570::~~online~win2003~x64~
        # wfn:[part="a",vendor="hp",product="insight_diagnostics", version="7\.4\.0\.1570",update=ANY,edition=ANY, sw_edition="online",target_sw="win2003",target_hw="x64", other=ANY,language=ANY]
        cpe_uri = 'cpe:/a:hp:insight_diagnostics:7.4.0.1570::~~online~win2003~x64~'
        expected_wfn_document = {'part': 'a', 'vendor': 'hp', 'product': 'insight_diagnostics',
                                 'version': '7.4.0.1570', 'update': 'ANY', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'online',	'target_sw': 'win2003', 'target_hw': 'x64', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # normally, tildes (~) are encoded to (%7e). However, if for some reason encoding was not performed
        # during the creation of the CPE URI, we have to consider this case and create the corresponding WFN correctly.

        cpe_uri = 'cpe:/a:hp:string_value_with\~:7.4.0.1570::~~online~win2003~x64~'
        expected_wfn_document = {'part': 'a', 'vendor': 'hp', 'product': 'string_value_with~',
                                 'version': '7.4.0.1570', 'update': 'ANY', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'online', 'target_sw': 'win2003', 'target_hw': 'x64', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 5
        # cpe:/a:hp:openview_network_manager:7.51:-:~~~linux~~
        # wfn:[part="a",vendor="hp",product="openview_network_manager", version="7\.51",update=NA,edition=ANY,sw_edition=ANY, target_sw="linux",target_HW=ANY,other=ANY,language=ANY]

        cpe_uri = 'cpe:/a:hp:openview_network_manager:7.51:-:~~~linux~~'
        expected_wfn_document = {'part': 'a', 'vendor': 'hp', 'product': 'openview_network_manager',
                                 'version': '7.51', 'update': 'NA', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'linux', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 6
        # cpe:/a:foo%5cbar:big%24money_2010%07:::~~special~ipod_touch~80gb~

        cpe_uri = 'cpe:/a:foo%5cbar:big%24money_2010%07:::~~special~ipod_touch~80gb~'
        expected_wfn_document = {'part': 'a', 'vendor': 'foo\\bar', 'product': 'big$money_2010%07',
                                 'version': 'ANY', 'update': 'ANY', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'special', 'target_sw': 'ipod_touch', 'target_hw': '80gb', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 7
        # cpe:/a:foo~bar:big%7emoney_2010
        # wfn:[part="a",vendor="foo\~bar",product="big\~money_2010", version=ANY,update=ANY,edition=ANY,language=ANY]

        cpe_uri = 'cpe:/a:foo~bar:big%7emoney_2010'
        expected_wfn_document = {'part': 'a', 'vendor': 'foo~bar', 'product': 'big~money_2010',
                                 'version': 'ANY', 'update': 'ANY', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # Example 8
        # cpe:/a:foo:bar:12.%02.1234

        cpe_uri = 'cpe:/a:foo:bar:12.%02.1234'
        expected_wfn_document = {'part': 'a', 'vendor': 'foo', 'product': 'bar',
                                 'version': '12.*.1234', 'update': 'ANY', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        # taken from official-cpe-dictionary_v2.3.xml

        cpe_uri = 'cpe:/a:mcafee:advanced_threat_defense:3.4.4.14'
        expected_wfn_document = {'part': 'a', 'vendor': 'mcafee', 'product': 'advanced_threat_defense',
                                 'version': '3.4.4.14', 'update': 'ANY', 'edition': 'ANY', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:mbtcreations:detox_juicing_diet_recipes:1.1::~~~android~~'
        expected_wfn_document = {'part': 'a', 'vendor': 'mbtcreations', 'product': 'detox_juicing_diet_recipes',
                                 'version': '1.1', 'update': 'ANY', 'edition': 'ANY', 'sw_edition': 'ANY',
                                 'target_sw': 'android', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:lemonldap-ng:lemonldap%3a%3a:1.0:rc2'
        expected_wfn_document = {'part': 'a', 'vendor': 'lemonldap-ng', 'product': 'lemonldap::',
                                 'version': '1.0', 'update': 'rc2', 'edition': 'ANY', 'sw_edition': 'ANY',
                                 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

    def test_convert_cpe_uri_to_wfn_no_edition_special_case(self):
        cpe_uri = 'cpe:/a:vendor:product:version:update:edition:language'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'update', 'edition': 'edition', 'language': 'language',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:vendor:product:version:update::language'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'update', 'edition': 'ANY', 'language': 'language',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:vendor:product:version:update:edition'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'update', 'edition': 'edition', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}

        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

    def test_convert_cpe_uri_to_wfn_edition_special_case(self):
        cpe_uri = 'cpe:/a:vendor:product:version:update:~edition~~~~'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'update', 'edition': 'edition', 'language': 'ANY',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:vendor:product:version:update:language~edition~~~~'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'update', 'edition': 'edition', 'language': 'language',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:vendor:product:version:-:language~edition~~~~'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'NA', 'edition': 'edition', 'language': 'language',
                                 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY', 'other': 'ANY'}
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

        cpe_uri = 'cpe:/a:vendor:product:version:update:language~edition~sw_edition~target_sw~target_hw~other'

        expected_wfn_document = {'part': 'a', 'vendor': 'vendor', 'product': 'product',
                                 'version': 'version', 'update': 'update', 'edition': 'edition', 'language': 'language',
                                 'sw_edition': 'sw_edition', 'target_sw': 'target_sw', 'target_hw': 'target_hw', 'other': 'other'}
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(cpe_uri)
        self.assert_wfn_docs_equal(expected_wfn_document, wfn)

    def test_convert_wfn_to_cpe_uri_binding(self):
        # example 1 (pag. 2. CPE: Naming Specification Version)
        # wfn:[part="a",vendor="microsoft",product="internet_explorer", version="8\.0\.6001",update="beta",edition=ANY]
        wfn = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer', 'version': '8.0.6001',
               'update': 'beta', 'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY',
               'other': 'ANY', 'language': 'ANY'}
        expected_uri = 'cpe:/a:microsoft:internet_explorer:8.0.6001:beta'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))

        # example 3 (pag. 2. CPE: Naming Specification Version)
        # wfn:[part="a",vendor="hp",product="insight_diagnostics", version="7\.4\.0\.1570",update=NA,
        # sw_edition="online",target_sw="win2003",target_hw="x64"]

        wfn = {'part': 'a', 'vendor': 'hp', 'product': 'insight_diagnostics', 'version': '7.4.0.1570',
               'update': 'NA', 'edition': 'ANY', 'sw_edition': 'online', 'target_sw': 'win2003', 'target_hw': 'x64',
               'other': 'ANY', 'language': 'ANY'}

        expected_uri = 'cpe:/a:hp:insight_diagnostics:7.4.0.1570:-:~~online~win2003~x64~'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))

        # example 4 (pag. 2. CPE: Naming Specification Version)
        # wfn:[part="a",vendor="hp",product="openview_network_manager", version="7\.51",target_sw="linux"]

        wfn = {'part': 'a', 'vendor': 'hp', 'product': 'openview_network_manager', 'version': '7.51',
               'update': 'ANY', 'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'linux', 'target_hw': 'ANY',
               'other': 'ANY', 'language': 'ANY'}

        expected_uri = 'cpe:/a:hp:openview_network_manager:7.51::~~~linux~~'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))

        # example 5 (pag. 2. CPE: Naming Specification Version)
        # wfn:[part="a",vendor="foo\\bar",product="big\$money_manager_2010", sw_edition="special",target_sw="ipod_touch",target_hw="80gb"]

        wfn = {'part': 'a', 'vendor': 'foo\\bar', 'product': 'big$money_manager_2010', 'version': 'ANY',
               'update': 'ANY', 'edition': 'ANY', 'sw_edition': 'special', 'target_sw': 'ipod_touch',
               'target_hw': '80gb', 'other': 'ANY', 'language': 'ANY'}

        expected_uri = 'cpe:/a:foo%5cbar:big%24money_manager_2010:::~~special~ipod_touch~80gb~'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))


    def test_convert_wfn_with_special_chars_to_cpe_uri_binding(self):
        # example 2 (pag. 2. CPE: Naming Specification Version)
        # wfn:[part="a",vendor="microsoft",product="internet_explorer", version="8\.*",update="sp?"]
        # Special Chars in WFN: * amd ?
        # The CPE specification assigns different codes to /* and * and /? and ?. Since we do not use / to scape
        # characters, the characters * and ? have each one two possible codes.

        wfn = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer', 'version': '8.*',
               'update': 'sp?', 'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY', 'target_hw': 'ANY',
               'other': 'ANY', 'language': 'ANY'}
        expected_uri_1 = 'cpe:/a:microsoft:internet_explorer:8.%02:sp%01'
        expected_uri_2 = 'cpe:/a:microsoft:internet_explorer:8.%2a:sp%01'
        expected_uri_3 = 'cpe:/a:microsoft:internet_explorer:8.%02:sp%3f'
        expected_uri_4 = 'cpe:/a:microsoft:internet_explorer:8.%2a:sp%3f'

        assert_1 = expected_uri_1 == self.wfn_converter.convert_wfn_to_uri(wfn)
        assert_2 = expected_uri_2 == self.wfn_converter.convert_wfn_to_uri(wfn)
        assert_3 = expected_uri_3 == self.wfn_converter.convert_wfn_to_uri(wfn)
        assert_4 = expected_uri_4 == self.wfn_converter.convert_wfn_to_uri(wfn)
        self.assertTrue(assert_1 or assert_2 or assert_3 or assert_4)

    def test_convert_wfn_to_cpe_uri_binding_special_case(self):
        wfn = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer', 'version': '8.0.6001',
               'update': 'beta', 'edition': 'edition_value', 'sw_edition': 'ANY', 'target_sw': 'windows',
               'target_hw': 'ANY', 'other': 'ANY', 'language': 'ANY'}
        expected_uri = 'cpe:/a:microsoft:internet_explorer:8.0.6001:beta:~edition_value~~windows~~'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))

        wfn = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer', 'version': '8.0.6001',
               'update': 'beta', 'edition': 'edition_value', 'sw_edition': 'ANY', 'target_sw': 'windows',
               'target_hw': 'ANY', 'other': 'ANY', 'language': 'language'}
        expected_uri = 'cpe:/a:microsoft:internet_explorer:8.0.6001:beta:language~edition_value~~windows~~'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))

        wfn = {'part': 'a', 'vendor': 'microsoft', 'product': 'internet_explorer', 'version': '8.0.6001',
               'update': 'beta', 'edition': 'NA', 'sw_edition': 'NA', 'target_sw': 'windows', 'target_hw': 'NA',
               'other': 'NA', 'language': 'language'}
        expected_uri = 'cpe:/a:microsoft:internet_explorer:8.0.6001:beta:language~-~-~windows~-~-'
        self.assertEqual(expected_uri, self.wfn_converter.convert_wfn_to_uri(wfn))

    def test_create_wfn_from_user_input(self):
        user_input = {'other': ['ANY'], 'target_hw': ['ANY'], 'vendor': ['microsoft'], 'update': ['sp1'],
                      'language': ['de'], 'sw_edition': ['ANY'], 'product': ['visual_foxpro'], 'target_sw': ['windows'],
                      'version': ['9.0.30729.6161'], 'part': ['a'],
                      'csrfmiddlewaretoken': ['G2Tg4v6Lo7pZ1bnIrz5b6X37jysLMTYH'], 'edition': ['ANY']}

        expected_wfn = {'part': 'a', 'vendor': 'microsoft', 'target_sw': 'windows', 'product': 'visual_foxpro',
                        'target_hw': 'ANY', 'update': 'sp1', 'version': '9.0.30729.6161', 'sw_edition': 'ANY',
                        'language': 'de', 'edition': 'ANY', 'other': 'ANY'}
        wfn = self.wfn_converter.create_wfn_from_user_input(user_input)
        self.test_utils.assertEqualKeys(expected_wfn, wfn)
        self.test_utils.assertEqualValues(expected_wfn, wfn)

    def assert_wfn_docs_equal(self, expected_wfn_document, wfn):
        self.assertIsNotNone(wfn)
        self.test_utils.assertEqualKeys(expected_wfn_document, wfn)
        self.test_utils.assertEqualValues(expected_wfn_document, wfn)


if __name__ == '__main__':
    unittest.main()