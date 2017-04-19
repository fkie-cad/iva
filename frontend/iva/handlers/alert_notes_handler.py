from django.http import HttpResponse
from django.template import loader

from alerts.alerts import Alerts
from .request_handler_utils import *

template = loader.get_template('iva/alert_notes.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        return get_handler.create_http_response()
    elif is_post_request(request):
        post_request = PostHandler(request)
        post_request.handle_post_request()
        return post_request.create_http_response()


class GetHandler:
    def __init__(self, request):
        self.request = request
        self.software_id = self.request.GET.get('software_id')
        self.notes = self.request.GET.get('notes')

    def create_http_response(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def create_context(self):
        return {'notes': self.notes, 'software_id': self.software_id}


class PostHandler:

    def __init__(self, request):
        self.alerts = Alerts()
        self.request = request
        self.item_id = self.request.POST.get('software_id')
        self.notes = self.request.POST.get('notes')

    def handle_post_request(self):
        self.alerts.update_notes(self.item_id, self.notes)

    @staticmethod
    def create_http_response():
        return HttpResponse('<script type="text/javascript">window.close(); '
                            'window.opener.parent.location.href = "/iva/alerts";</script>')