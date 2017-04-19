from django.http import HttpResponse
from django.template import loader
from inventory.inventory import Inventory
from inventory.software_cve_matches import CVEMatches
from matching.cve_matcher import CVEMatcher
from .request_handler_utils import *
import config

template = loader.get_template('iva/search_cves.html')


def handle_request(request):

    if is_get_request(request):
        get_handler = GetHandler(request)
        get_handler.handle_get_request()
        context = get_handler.create_context()
        return get_handler.create_http_response(context)
    elif is_post_request(request):
        post_handler = PostHandler()
        return post_handler.create_http_response()


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.cve_matches = CVEMatches()
        self.cve_matcher = CVEMatcher()
        self.uri_binding = self.get_uri_binding_from_get_request()
        self.software_id = self.get_software_id_from_get_request()

    def create_http_response(self, context):
        return HttpResponse(template.render(context, self.request))

    def handle_get_request(self):
        pass

    def get_uri_binding_from_get_request(self):
        return self.request.GET.get('uri_binding')

    def get_software_id_from_get_request(self):
        return self.request.GET.get('software_id')

    def get_option_from_get_request(self):
        return self.request.GET.get('option')

    def get_cve_id_from_get_request(self):
        return self.request.GET.get('cve_id')

    def create_context(self):
        return {'cve_matches': self.get_cpe_cve_matches(),
                'uri_binging': self.uri_binding,
                'software_id': self.software_id,
                'software': self.get_software(),
                'cve_search_url': config.get_cve_search_url()}

    def get_cpe_cve_matches(self):
        matches = self.search_matches()
        self.insert_new_matches(matches)
        return self.get_new_matches()

    def search_matches(self):
        return self.cve_matcher.search_cves_for_cpe(self.uri_binding)

    def insert_new_matches(self, matches):
        self.cve_matches.insert_software_cve_matches(self.software_id, matches)

    def get_new_matches(self):
        return self.cve_matches.get_software_cve_matches(self.software_id)

    def get_software(self):
        return Inventory().get_software_by_id(self.software_id)


class PostHandler:

    def __init__(self):
        pass

    @staticmethod
    def create_http_response():
        return HttpResponse('POST Request made', content_type="text/plain")
