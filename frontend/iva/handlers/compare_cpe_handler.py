from django.http import HttpResponse
from django.template import loader
from .request_handler_utils import *
from wfn.wfn_converter import WFNConverter
from wfn.wfn_comparator import compare_wfn

template = loader.get_template('iva/compare_cpe.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        return get_handler.create_http_response()


wfn_converter = WFNConverter()


class GetHandler:

    def __init__(self, request):
        self.request = request

    def create_http_response(self):
        context = self.create_context()
        return HttpResponse(template.render(context, self.request))

    def create_context(self):
        wfn_a = self.get_wfn_from_get_request('uri_binding_a')
        wfn_b = self.get_wfn_from_get_request('uri_binding_b')
        result = compare_wfn(wfn_a, wfn_b)
        return {'wfn_a': wfn_a, 'wfn_b': wfn_b, 'coincidence': result.get('coincidence_rate'),
                'not_matches': result.get('not_matches')}

    def get_wfn_from_get_request(self, get_request_key):
        uri_binding = self.request.GET.get(get_request_key)
        return wfn_converter.convert_cpe_uri_to_wfn(uri_binding)
