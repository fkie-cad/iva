import editdistance
from database import Database
from inventory.inventory import Inventory
from wfn.wfn_converter import WFNConverter
from local_repositories.cve_feeds import IVA_CVE_COLLECTION


class CVEMatcher:

    def __init__(self):
        self.db = Database()
        self.wfn_converter = WFNConverter()
        self.inventory = Inventory()

    def search_cves_for_cpe(self, uri_binding):
        wfn = self.wfn_converter.convert_cpe_uri_to_wfn(uri_binding)
        matches_a = self.search_cves(wfn)
        matches_b = self.search_cves_with_summary(wfn)
        merge_lists(matches_a, matches_b)
        return matches_a

    def search_cves(self, wfn):
        cve_matches = []
        for vendor in self.get_vendor_candidates(wfn):
            for product in self.get_product_candidates(wfn):
                tmp_cve_matches = self.search_cves_by_product_and_vendor(product, vendor)
                filtered_matches = filter_cpe_entries_in_cve_matches_by_version(tmp_cve_matches, wfn)
                cve_matches.extend(filtered_matches)
        return cve_matches

    def get_vendor_candidates(self, wfn):
        candidates = []
        wfn_vendor = get_vendor_from_wfn(wfn)
        for v in self.inventory.get_vendors():
            if are_strings_similar(v, wfn_vendor):
                candidates.append(v)
        return candidates

    def get_product_candidates(self, wfn):
        candidates = []
        wfn_product = get_product_from_wfn(wfn)
        for p in self.inventory.get_products():
            if are_strings_similar(p, wfn_product):
                candidates.append(p)
        wfn_vendor = get_vendor_from_wfn(wfn)
        if wfn_vendor in wfn_product:
            candidates.append(remove_vendor_from_product(wfn_product, wfn_vendor))
        else:
            candidates.append(add_vendor_to_product(wfn_vendor, wfn_product, 'left'))
            candidates.append(add_vendor_to_product(wfn_vendor, wfn_product, 'right'))
        return candidates

    def search_cves_by_product_and_vendor(self, product, vendor):
        search_condition = create_search_condition(product, vendor)
        aggregation = create_aggregation(product, vendor)
        return self.db.search_documents_and_aggregate(search_condition, aggregation, IVA_CVE_COLLECTION)

    def search_cves_with_summary(self, wfn):
        matches = []
        for cve in self.get_cve_without_cpe_entries():
            if is_product_and_vendor_in_cve_summary(cve, wfn):
                matches.append(cve)
        return matches

    def get_cve_without_cpe_entries(self):
        return self.db.search_documents_in_collection({'cpe_entries': {'$size': 0}}, IVA_CVE_COLLECTION)


def is_product_and_vendor_in_cve_summary(cve, wfn):
    summary_words = get_summary_words(cve)
    return is_word_in_summary(get_vendor_from_wfn(wfn), summary_words) and \
           is_word_in_summary(get_product_from_wfn(wfn), summary_words)


def is_word_in_summary(word, summary_words):
    for s_word in summary_words:
        if are_strings_similar(word, s_word):
            return True
    return False


def filter_cpe_entries_in_cve_matches_by_version(cve_matches, wfn):
    filtered_matches = []
    for cve_match in cve_matches:
        updated_cpe_entries = []
        for cve_cpe in get_cpes_from_cve(cve_match):
            if is_main_version_equal(cve_cpe, wfn):
                updated_cpe_entries.append(cve_cpe)
        if len(updated_cpe_entries) > 0:
            cve_match.update({'cpe_entries': updated_cpe_entries})
            filtered_matches.append(cve_match)
    return filtered_matches


def get_cpes_from_cve(cve):
    return cve.get('cpe_entries')


def create_search_condition(product, vendor):
    return {'cpe_entries': {'$elemMatch': {'$and': [{'wfn.product': product}, {'wfn.vendor': vendor}]}}}


def create_aggregation(product, vendor):
    return {'cpe_entries': {'$filter': create_aggregation_filter(product, vendor)}, '_id': 0, 'cve_id': 1, 'cve_summary': 1}


def create_aggregation_filter(product, vendor):
    return {'input': '$cpe_entries', 'as': 'cpe_entries',
            'cond': {'$and': [{'$eq': ['$$cpe_entries.wfn.product', product]},
                              {'$eq': ['$$cpe_entries.wfn.vendor', vendor]}]}}


def is_same_version(cve_cpe, wfn):
    return cve_cpe.get('wfn').get('version') == wfn.get('version')


def is_main_version_equal(cve_cpe, wfn):
    return is_version_any(wfn) or get_main_version(cve_cpe.get('wfn')) == get_main_version(wfn)


def is_version_any(wfn):
    main_ver = get_main_version(wfn)
    return main_ver == '*' or main_ver == 'ANY'


def get_main_version(wfn):
    return wfn.get('version').split('.')[0]


def merge_lists(list_a, list_b):
    for e in list_b:
        if e not in list_a:
            list_a.append(e)


def are_strings_similar(string_a, string_b):
    return editdistance.eval(string_a, string_b) <= 2


def get_vendor_from_wfn(wfn):
    return wfn.get('vendor').lower()


def get_product_from_wfn(wfn):
    return wfn.get('product').lower()


def get_summary_words(cve):
    summary = str(cve.get('cve_summary')).lower()
    summary_words = summary.split()
    return summary_words


def remove_vendor_from_product(product, vendor):
    product_without_vendor = product.replace(vendor, '')
    product_without_vendor = product_without_vendor.replace('_', '')
    return product_without_vendor


def add_vendor_to_product(vendor, product, position):
    if position == 'left':
        return vendor + '_' + product
    return product + '_' + vendor
