import editdistance
from local_repositories.cpe_dict import IVA_CPE_COLLECTION
from matching.search_terms_generator import generate_product_search_terms
from matching.search_terms_generator import remove_version_from_search_terms
from matching.search_terms_generator import generate_vendor_filters
from matching.software_formatter import FormattedSoftware
from database import Database
from matching import cpe_sorter
from wfn.wfn_converter import WFNConverter
import jellyfish

class CPEMatcher:

    def __init__(self):
        self.db = Database()
        self.wfn_creator = WFNConverter()

    def search_cpes_for_software(self, software):
        formatted_sw = FormattedSoftware(software)
        product_search_terms = generate_product_search_terms(formatted_sw.product, formatted_sw.vendor)
        version = formatted_sw.get_version(product_search_terms)
        product_search_terms = remove_version_from_search_terms(product_search_terms, version)

        candidates = self.search_cpe_candidates_by_product(product_search_terms)
        filtered_candidates = filter_cpe_candidates_by_vendor(candidates, formatted_sw.vendor, product_search_terms)
        ordered_candidates = sort_cpe_candidates_by_version(filtered_candidates, version, product_search_terms)
        return ordered_candidates

    def search_cpe_candidates_by_product(self, product_search_terms):
        candidates = get_cpe_candidates_dict_ordered_by_search_terms(product_search_terms)
        for cpe in self.get_cpe_dictionary():
            wfn_product = cpe.get('wfn').get('product')
            for search_term in product_search_terms:
                if are_strings_similar(wfn_product, search_term) and (cpe not in candidates.get(search_term)):
                    candidates.get(search_term).append(cpe)
                    break
        return candidates

    def get_cpe_dictionary(self):
        return self.db.get_documents_from_collection(IVA_CPE_COLLECTION)


def get_cpe_candidates_dict_ordered_by_search_terms(product_search_terms):
    st_cpes = {}
    for search_term in product_search_terms:
        st_cpes[search_term] = []
    return st_cpes


def filter_cpe_candidates_by_vendor(candidates, vendor, product_search_terms):
    for search_term in product_search_terms:
        candidates[search_term] = filter_by_vendor(candidates[search_term], vendor)
    return candidates


def filter_by_vendor(cpes, vendor):
    filtered_cpe_matches = []
    for cpe in cpes:
        for filter_ in generate_vendor_filters(vendor):
            wfn_vendor = dict(cpe).get('wfn').get('vendor')
            if are_strings_similar(filter_, wfn_vendor):
                filtered_cpe_matches.append(cpe)
    return filtered_cpe_matches


def sort_cpe_candidates_by_version(candidates, version, product_search_terms):
    all_sorted_candidates = []
    for search_term in product_search_terms:
        sorted_candidates = cpe_sorter.sort_cpes_by_version(candidates.get(search_term), version)
        all_sorted_candidates.extend(sorted_candidates)
    return all_sorted_candidates


def are_strings_similar(string_a, string_b):
    d = jellyfish.jaro_winkler(string_a, string_b)
    return d >= 0.9