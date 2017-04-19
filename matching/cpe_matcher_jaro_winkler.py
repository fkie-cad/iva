import editdistance
from local_repositories.cpe_dict import IVA_CPE_COLLECTION
from matching.search_terms_generator import generate_product_search_terms
from matching.search_terms_generator import remove_version_from_search_terms
from matching.search_terms_generator import generate_vendor_filters
from matching.software_formatter import FormattedSoftware
from database import Database
from matching import cpe_sorter
import jellyfish
from wfn.wfn_converter import WFNConverter


class CPEMatcher:

    def __init__(self):
        self.db = Database()
        self.wfn_creator = WFNConverter()

    def search_cpes_for_software(self, software):
        formatted_sw = FormattedSoftware(software)
        product_search_terms = generate_product_search_terms(formatted_sw.product, formatted_sw.vendor)
        version = formatted_sw.get_version(product_search_terms)
        # product_search_terms = remove_version_from_search_terms(product_search_terms, version)

        candidates = self.search_cpe_candidates_by_product(formatted_sw.product)
        filtered_candidates = filter_cpe_candidates_by_vendor(candidates, formatted_sw.vendor)
        sorted_candidates = cpe_sorter.sort_cpes_by_version(filtered_candidates, version)
        return sorted_candidates

    def search_cpe_candidates_by_product(self, product):
        candidates = []
        for cpe in self.get_cpe_dictionary():
            wfn_product = cpe.get('wfn').get('product')
            if are_strings_similar(product, wfn_product) and (cpe not in candidates):
                candidates.append(cpe)
        return candidates

    def get_cpe_dictionary(self):
        return self.db.get_documents_from_collection(IVA_CPE_COLLECTION)


def filter_cpe_candidates_by_vendor(candidates, vendor):
    filtered_cpe_matches = []
    for candidate in candidates:
        wfn_vendor = candidate.get('wfn').get('vendor')
        if are_strings_similar(vendor, wfn_vendor):
            filtered_cpe_matches.append(candidate)
    return filtered_cpe_matches


def are_strings_similar(string_a, string_b):
    d = jellyfish.jaro_winkler(string_a, string_b)
    # print(string_a + "==" + string_b + ':' + str(d))
    return d >= 0.9
