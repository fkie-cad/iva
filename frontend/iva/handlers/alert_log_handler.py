from django.http import HttpResponse
from django.template import loader
from .request_handler_utils import *

template = loader.get_template('iva/alert_log.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        return get_handler.create_http_response()


class GetHandler:
    def __init__(self, request):
        self.request = request

    def create_http_response(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def create_context(self):
        return {'log': ast.literal_eval(self.request.GET.get('log'))}
