from django.http import HttpResponse
from django.template import loader
from .request_handler_utils import *
from wfn.wfn_converter import WFNConverter

template = loader.get_template('iva/cpe_wfn.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        return get_handler.create_http_response()


class GetHandler:
    def __init__(self, request):
        self.request = request

    def create_http_response(self):
        context = self.create_context()
        return HttpResponse(template.render(context, self.request))

    def create_context(self):
        wfn_converter = WFNConverter()
        uri_binding = self.request.GET.get('uri_binding')
        return {'uri_binging': uri_binding, 'wfn': wfn_converter.convert_cpe_uri_to_wfn(uri_binding)}
