from django.http import HttpResponse
from django.template import loader
from config import get_cve_search_url
from inventory.inventory import Inventory
from .request_handler_utils import *
from inventory.software_cve_matches import CVEMatches

TEMPLATE = loader.get_template('iva/grouped_cve_matches.html')


def handle_request(request):
    handler = get_handler(request)
    handler.handle_request()
    return handler.create_http_response()


def get_handler(request):
    if is_get_request(request):
        return GetHandler(request)
    return PostHandler(request)


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.software_id = self.request.GET.get('software_id')
        self.cve_id = self.request.GET.get('cve_id')
        self.grouped_cve_matches = []
        self.software = {}

    def handle_request(self):
        self.software = self.get_software()
        self.grouped_cve_matches = self.get_grouped_matches()

    def get_grouped_matches(self):
        return CVEMatches().get_software_cve_matches_with_same_cpe_entries_as_cve(self.software_id, self.cve_id)

    def get_software(self):
        return Inventory().get_software_by_id(self.software_id)

    def create_http_response(self):
        return HttpResponse(TEMPLATE.render(self.create_response_context(), self.request))

    def create_response_context(self):
        return {'cve_matches': self.grouped_cve_matches,
                'software': self.software,
                'cve_search_url': get_cve_search_url()}


class PostHandler:

    def __init__(self, request):
        self.cve_matches = CVEMatches()
        self.request = request
        self.software_id = self.post_value('software_id')
        self.cve_id_master = self.post_value('cve_id_master')
        self.option = self.post_value('option')

    def handle_request(self):
        if self.option == 'set_group_as_positive':
            self.set_group_as_positive()
        elif self.option == 'set_group_as_negative':
            self.set_group_as_negative()
        elif self.option == 'set_group_as_removed':
            self.set_group_as_removed()
        elif self.option == 'restore_group':
            self.restore_group()

    def set_group_as_positive(self):
        self.cve_matches.set_cve_matches_group_as_positive(self.software_id, self.cve_id_master)

    def set_group_as_negative(self):
        self.cve_matches.set_cve_matches_group_as_negative(self.software_id, self.cve_id_master)

    def set_group_as_removed(self):
        self.cve_matches.set_cve_matches_group_as_removed(self.software_id, self.cve_id_master)

    def restore_group(self):
        self.cve_matches.restore_cve_matches_group(self.software_id, self.cve_id_master)

    def create_http_response(self):
        return HttpResponse('OK')

    def post_value(self, key):
        return self.request.POST.get(key)


