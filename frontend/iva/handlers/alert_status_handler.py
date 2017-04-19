from django.http import HttpResponse
from django.template import loader
from alerts.alerts import Alerts
from inventory.software_cve_matches import CVEMatches
from .request_handler_utils import *
from alerts.alerts import STATUS

template = loader.get_template('iva/alert_status.html')


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
        self.current_status = self.request.GET.get('current_status')
        self.software_id = self.request.GET.get('software_id')

    def create_http_response(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def create_context(self):
        return {'software_id': self.software_id, 'current_status': self.current_status, 'status_list': self.get_status_list()}

    def get_status_list(self):
        status_list = list(STATUS)
        status_list.remove(self.current_status)
        return status_list


class PostHandler:

    def __init__(self, request):
        self.alerts = Alerts()
        self.cve_matches = CVEMatches()
        self.request = request
        self.software_id = self.request.POST.get('software_id')
        self.new_status = self.request.POST.get('new_status')

    def handle_post_request(self):
        self.set_cves_as_negatives()
        self.alerts.change_alert_status(self.software_id, self.new_status)

    def set_cves_as_negatives(self):
        if self.new_status == 'removed':
            alert = self.alerts.get_software_alert(self.software_id)
            for cve in alert.get('cves'):
                self.cve_matches.set_cve_match_as_negative(self.software_id, cve)

    @staticmethod
    def create_http_response():
        return HttpResponse('<script type="text/javascript">window.close(); '
                            'window.opener.parent.location.href = "/iva/alerts";</script>')
