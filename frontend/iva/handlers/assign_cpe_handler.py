from copy import copy

import pycountry
from django.http import HttpResponse
from django.template import loader
from inventory.software_cpe import SoftwareCPE
from matching.cpe_matcher import CPEMatcher
from inventory.inventory import Inventory
from wfn.wfn_converter import WFNConverter
from .request_handler_utils import *
from django.http import JsonResponse
from wfn.encoding import Decoder
from matching.software_formatter import FormattedSoftware

template = loader.get_template('iva/assign_cpe.html')
software_cpe_template = loader.get_template('iva/sw_products_with_cpe.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        http_response = get_handler.handle_request()
        return http_response
    elif is_post_request(request):
        post_handler = PostHandler(request)
        return post_handler.handle_request()


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.software = self.get_software()
        self.cpe_candidates = self.get_cpe_matches_for_software()

    def get_software(self):
        return Inventory().get_software_by_id(self.request.GET.get('id'))

    def get_cpe_matches_for_software(self):
        return CPEMatcher().search_cpes_for_software(self.software)

    def handle_request(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def create_context(self):
        return {'software': self.software,
                'software_id': self.software.get('id'),
                'cpe_matches': self.cpe_candidates,
                'wfn': self.get_wfn_of_best_cpe_candidate(),
                'lang_codes': pycountry.languages}

    def get_wfn_of_best_cpe_candidate(self):
        if len(self.cpe_candidates) > 0:
            return self.get_wfn_of_best_cpe_candidate_from_cpe_candidates()
        return self.create_best_cpe_candidate_from_software_info()

    def get_wfn_of_best_cpe_candidate_from_cpe_candidates(self):
        best_candidate = copy(self.cpe_candidates[0])
        self.update_wfn_version_of_best_cpe_candidate(best_candidate)
        return best_candidate.get('wfn')

    def update_wfn_version_of_best_cpe_candidate(self, best_cpe_candidate):
        sw_version = get_version_from_dict(self.software)
        best_cpe_candidate_wfn = get_wfn_from_cpe(best_cpe_candidate)
        best_cpe_candidate_version = get_version_from_dict(best_cpe_candidate_wfn)
        if (best_cpe_candidate_version != sw_version) and (sw_version != ''):
            update_wfn_version(sw_version, best_cpe_candidate_wfn)
            update_wfn_in_cpe(best_cpe_candidate, best_cpe_candidate_wfn)

    def create_best_cpe_candidate_from_software_info(self):
        formatted_software = FormattedSoftware(self.software)
        return {'part': 'a',
                'vendor': formatted_software.vendor,
                'product': formatted_software.product,
                'version': self.software.get('version'),
                'update': 'ANY', 'edition': 'ANY', 'language': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'ANY',
                'target_hw': 'ANY', 'other': 'ANY'}


class PostHandler:

    def __init__(self, request):
        self.sw_cpe = SoftwareCPE()
        self.wfn_converter = WFNConverter()
        self.inventory = Inventory()
        self.request = request
        self.decoder = Decoder()

    def handle_request(self):
        if not self.request.POST.get('check'):
            sw_cpe_dict = self.sw_cpe.create_sw_cpe_dict(self.get_wfn())
            self.sw_cpe.assign_cpe_to_software(sw_cpe_dict, self.get_software_id())
            return self.create_http_response_for_add_cpe(sw_cpe_dict)
        return self.create_http_response_for_verify_cpe_exists()

    def get_wfn(self):
        return self.wfn_converter.create_wfn_from_user_input(self.request.POST)

    def get_software_id(self):
        return self.request.POST.get('software_id')

    def create_http_response_for_verify_cpe_exists(self):
        uri = self.wfn_converter.convert_wfn_to_uri(self.get_wfn())
        software = self.sw_cpe.get_software_cpe_by_uri(uri)
        if software is not None:
            return JsonResponse({'result': 'exist', 'uri_binding': self.decoder.decode_non_alphanumeric_characters(uri)})
        return JsonResponse({'result': 'not_exist', 'uri_binding': self.decoder.decode_non_alphanumeric_characters(uri)})

    def create_http_response_for_add_cpe(self, cpe_doc):
        return HttpResponse(software_cpe_template.render({'inventory': self.inventory.get_software_products_with_assigned_cpe(),
                                                          'updated': cpe_doc.get('uri_binding')}, self.request))


def update_wfn_in_cpe(cpe, wfn):
    cpe.update({'wfn': wfn})


def update_wfn_version(software_version, wfn):
    wfn.update({'version': software_version})


def get_version_from_dict(dict_):
    return dict_.get('version')


def get_wfn_from_cpe(cpe):
    return dict(cpe.get('wfn'))