import pycountry
from django.http import HttpResponse
from django.template import loader
from inventory.inventory import Inventory
from inventory.software_cpe import SoftwareCPE
from .request_handler_utils import *
from wfn.wfn_converter import WFNConverter

template = loader.get_template('iva/modify_cpe.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        return get_handler.create_http_response()
    elif is_post_request(request):
        post_handler = PostHandler(request)
        post_handler.handle_post_request()
        http_response = post_handler.create_http_response()
        return http_response


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.software_id = self.request.GET.get('software_id')

    def create_http_response(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def create_context(self):
        return get_context_dict(self.get_software(), update=False)

    def get_software(self):
        return Inventory().get_software_by_id(self.software_id)


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.software_id = self.request.POST.get('software_id')

    def handle_post_request(self):
        SoftwareCPE().update_software_cpe(self.software_id, self.get_wfn())

    def get_wfn(self):
        return WFNConverter().create_wfn_from_user_input(self.request.POST)

    def create_http_response(self):
        return HttpResponse(template.render(get_context_dict(self.get_software(), update=True), self.request))

    def get_software(self):
        return Inventory().get_software_by_id(self.software_id)


def get_wfn_from_sw(software):
    return software.get('cpe').get('wfn')


def get_uri_from_sw(software):
    return software.get('cpe').get('uri')


def get_context_dict(software, update):
    return {'software': software,
            'software_id': software.get('id'),
            'uri_binding': get_uri_from_sw(software),
            'wfn': get_wfn_from_sw(software),
            'updated': update,
            'lang_codes': pycountry.languages}