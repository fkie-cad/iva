class FormattedSoftware:
    def __init__(self, software):
        self.software = software

    @property
    def product(self):
        return format_product(self.software)

    @property
    def vendor(self):
        return format_vendor(self.software)

    def get_version(self, product_search_phrases):
        version = self.software.get('version')
        if version == '':
            return get_version_from_product_search_phrases(product_search_phrases)
        return version

    @property
    def os(self):
        return self.software.get('os')


def get_version_from_product_search_phrases(product_search_phrases):
    for search_phrase in product_search_phrases:
        if search_phrase.isdigit() and len(search_phrase) == 4:
            return search_phrase
    return ''


def format_product(software):
    return format_string(str(software.get('product')))


def format_vendor(software):
    return format_string(str(software.get('vendor')))


def format_string(string):
    formatted_str = replace_spaces_by_underscore(string)
    formatted_str = formatted_str.lower()
    formatted_str = replace_parenthesis_by_underscores(formatted_str)
    formatted_str = replace_double_underscore_by_one_underscore(formatted_str)
    formatted_str = remove_last_underscore(formatted_str)
    return formatted_str


def replace_spaces_by_underscore(string):
    return string.replace(' ', '_')


def replace_parenthesis_by_underscores(string):
    string = string.replace('(', '_')
    string = string.replace(')', '_')
    return string


def replace_double_underscore_by_one_underscore(string):
    return string.replace('__', '_')


def remove_last_underscore(string):
    if string[-1] == '_':
        return string[:-1]
    return string

