characters_map = {'%21': '!', '%22': '\"', '%23': '#', '%24': '$', '%25': '%', '%26': '&', '%27': '\'',
                  '%28': '(', '%29': ')', '%2a': '*',  '%2b': '+', '%2c': ',', '%2f': '/', '%3a': ':', '%3b': ';',
                  '%3c': '<', '%3d': '=', '%3e': '>', '%3f': '?', '%40': '@', '%5b': '[', '%5c': '\\', '%5d': ']',
                  '%5e': '^', '%60': '`', '%7b': '{', '%7c': '|', '%7d': '}',  '%7e': '~'}


class Encoder:

    @staticmethod
    def encode_escaped_double_points(string):
        return string.replace('\\:', '%3a')

    @staticmethod
    def encode_escaped_tildes(string):
        return string.replace('\\~', '%7e')

    @staticmethod
    def encode_non_alphanumeric_characters(string):
        string = string.replace(characters_map.get('%25'), '%25')
        for encoded_char in characters_map.keys():
            if characters_map.get(encoded_char) != '%':
                string = string.replace(characters_map.get(encoded_char), encoded_char)
        return string


class Decoder:

    @staticmethod
    def decode_non_alphanumeric_characters(string):
        string = decode_special_chars(string)
        for encoded_char in characters_map.keys():
            string = string.replace(encoded_char, characters_map.get(encoded_char))
        return string


def decode_special_chars(string):
    string = string.replace('%01', '?')
    string = string.replace('%02', '*')
    return string
