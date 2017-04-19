from wfn.encoding import Decoder, Encoder


class WFNConverter:

    def __init__(self):
        self.wfn_doc = {}
        self.wfn_keys = ['part', 'vendor', 'product', 'version', 'update', 'edition', 'language', 'sw_edition',
                         'target_sw', 'target_hw', 'other']
        self.wfn_keys_edition_special_case = ['part', 'vendor', 'product', 'version', 'update', 'language', 'edition',
                                              'sw_edition', 'target_sw', 'target_hw', 'other']

    def convert_cpe_uri_to_wfn(self, cpe_uri):
        self.set_wfn_default_values()
        cpe_uri = self.encode_cpe_uri(cpe_uri)
        wfn_values = self.get_wfn_values_from_cpe_uri(cpe_uri)
        self.set_wfn_values(wfn_values)
        return self.wfn_doc

    def set_wfn_default_values(self):
        self.wfn_doc = {'part': 'ANY', 'vendor': 'ANY', 'product': 'ANY', 'version': 'ANY', 'update': 'ANY',
                        'edition': 'ANY', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY',
                        'target_hw': 'ANY', 'other': 'ANY'}

    @staticmethod
    def encode_cpe_uri(cpe_uri):
        cpe_uri = Encoder.encode_escaped_double_points(cpe_uri)
        cpe_uri = Encoder.encode_escaped_tildes(cpe_uri)
        return cpe_uri

    @staticmethod
    def get_wfn_values_from_cpe_uri(cpe_uri):
        wfn_first_part, wfn_second_part = WFNConverter.get_wfn_parts(cpe_uri)
        wfn_values = WFNConverter.merge_wfn_parts(wfn_first_part, wfn_second_part)
        WFNConverter.clean_values(wfn_values)
        return wfn_values

    @staticmethod
    def clean_values(values):
        values.remove('cpe')  # discard 'cpe' value
        values[0] = WFNConverter.remove_slash_from_value(values[0])

    @staticmethod
    def get_wfn_parts(cpe_uri):
        first_part = cpe_uri.split(':')
        second_part = first_part[-1].split('~')
        return first_part, second_part

    @staticmethod
    def merge_wfn_parts(wfn_first_part, wfn_second_part):
        if len(wfn_second_part) > 1:
            lang = WFNConverter.get_lang_from_wfn_first_part(wfn_first_part)
            del wfn_first_part[-1]       # remove value of second part
            wfn_first_part.append(lang)
            del wfn_second_part[0]       # remove value of first part
            wfn_first_part.extend(wfn_second_part)
        return wfn_first_part

    @staticmethod
    def get_lang_from_wfn_first_part(first_part_values):
        return first_part_values[-1].split('~')[0]

    def set_wfn_values(self, wfn_values):
        wfn_keys_index = 0
        wfn_keys = self.get_wfn_keys(wfn_values)
        for wfn_value in wfn_values:
            wfn_value = Decoder.decode_non_alphanumeric_characters(wfn_value)
            wfn_key = wfn_keys[wfn_keys_index]
            self.set_wfn_value(wfn_key, wfn_value)
            wfn_keys_index += 1

    def get_wfn_keys(self, wfn_values):
        if len(wfn_values) > 7:
            return self.wfn_keys_edition_special_case
        return self.wfn_keys

    def set_wfn_value(self, key, value):
        if not self.is_value_any(value):
            if value == '-':
                self.set_wfn_value(key, 'NA')
            else:
                self.wfn_doc.__setitem__(key, value)

    @staticmethod
    def is_value_any(value):
        return value == '' or value == '*' or value == 'ANY'

    @staticmethod
    def remove_slash_from_value(wfn_value):
        return wfn_value.replace('/', '')

    def get_uri_binding_version(self, uri_binding):
        return self.convert_cpe_uri_to_wfn(uri_binding).get('version')

    def get_uri_binding_target_sw(self, uri_binding):
        return self.convert_cpe_uri_to_wfn(uri_binding).get('target_sw')

    def convert_wfn_to_uri(self, wfn):
        uri = 'cpe:/'
        special_case = self.is_wfn_special_case(wfn)
        if not special_case:
            uri_first_part_attributes = self.get_uri_first_part_attributes(wfn)
            uri += self.concat_uri_attributes(':', uri_first_part_attributes)
        else:
            uri_first_part_attributes = self.get_uri_first_part_attributes(wfn, True)
            uri += self.concat_uri_attributes(':', uri_first_part_attributes,  True)
            uri = self.concatenate_uri_second_part_attributes(uri, wfn)
        return uri

    def get_uri_first_part_attributes(self, wfn, edition_special_case=False):
        uri_first_part_attributes = []
        range_limit = 7
        wfn_keys = self.wfn_keys
        if edition_special_case:
            range_limit = 6
            wfn_keys = self.wfn_keys_edition_special_case
        for i in range(range_limit):
            uri_first_part_attributes.append(wfn.get(wfn_keys[i]))
        return uri_first_part_attributes

    def is_wfn_special_case(self, wfn):
        special_case = False
        for i in range(7, 11):
            attribute = wfn.get(self.wfn_keys[i])
            if not self.is_value_any(attribute):
                return True
        return special_case

    @staticmethod
    def concat_uri_attributes(splitter_char, attributes, edition_special_case=False):
        uri = ''
        if not edition_special_case:
            while WFNConverter.is_value_any(attributes[-1]):
                attributes.pop()
        for attribute in attributes:
            uri = WFNConverter.concat_uri_attribute(uri, attribute, splitter_char)
        return uri[:-1]

    def concatenate_uri_second_part_attributes(self, uri, wfn):
        uri += '~'
        for i in range(6, 11):
            uri_attribute = wfn.get(self.wfn_keys_edition_special_case[i])
            uri = self.concat_uri_attribute(uri, uri_attribute, '~')
        return uri[:-1]

    @staticmethod
    def concat_uri_attribute(uri, attribute, splitter_char):
        attribute = Encoder.encode_non_alphanumeric_characters(attribute)
        if attribute == 'NA':
            uri += '-' + splitter_char
        elif attribute != 'ANY':
            uri += attribute + splitter_char
        else:
            uri += splitter_char
        return uri

    def create_wfn_from_user_input(self, user_input):
        self.set_wfn_default_values()
        for key in self.wfn_keys:
            value = dict(user_input).get(key)
            if value is not None:
                self.set_wfn_value(key, value[0])
        return self.wfn_doc

