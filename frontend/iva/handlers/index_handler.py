from django.http import HttpResponse
from .request_handler_utils import *
from django.template import loader

template = loader.get_template('iva/index.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        context = get_handler.get_context_for_get_request()
        http_response = get_handler.create_http_response(context)
        return http_response


class GetHandler:
    def __init__(self, request):
        self.request = request

    def get_context_for_get_request(self):
        return {}

    def create_http_response(self, context):
        return HttpResponse(template.render(context, self.request))


