import config
from django.http import HttpResponse
from django.template import loader
from alerts.alerts import Alerts
from inventory.software_cve_matches import CVEMatches
from inventory.inventory import Inventory
from .request_handler_utils import *

template = loader.get_template('iva/alerts.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        get_handler.handle_get_request()
        return get_handler.create_http_response()

    elif is_post_request(request):
        post_handler = PostHandler(request)
        return post_handler.handle_post_request()


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.option = self.post_value('option')
        self.software_id = self.post_value('software_id')
        self.cve_id = self.post_value('cve_id')
        self.cve_matches = CVEMatches()
        self.alerts = Alerts()

    def handle_post_request(self):
        if self.option == 'set_cve_as_negative':
            self.cve_matches.set_cve_match_as_negative(self.software_id, self.cve_id)
        elif self.option == 'notify':
            was_sent = self.alerts.send_sw_alert_by_email(self.software_id)
            if not was_sent:
                return HttpResponse('failed')
        return HttpResponse('ok')

    def post_value(self, key):
        return self.request.POST.get(key)


class GetHandler:

    def __init__(self, request):
        self.alerts = Alerts()
        self.inventory = Inventory()
        self.request = request

    def create_http_response(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def handle_get_request(self):
        pass

    def create_context(self):
        return {'alerts': self.get_alerts(), 'cve_search_url': config.get_cve_search_url()}

    def get_alerts(self):
        alerts = self.alerts.get_alerts()
        for alert in alerts:
            self.add_cpe_to_alert(alert)
            format_alert_log(alert)
        return alerts

    def add_cpe_to_alert(self, alert):
        sw = self.inventory.get_software_by_id(alert.get('software_id'))
        if sw is not None:
            alert.update({'uri': sw.get('cpe').get('uri_binding')})
            alert.update({'product': sw.get('product')})
            alert.update({'vendor': sw.get('vendor')})
            alert.update({'version': sw.get('version')})
        else:
            alert.update({'product': 'product was removed from database'})


def format_alert_log(alert):
    log = []
    for entry in alert.get('log'):
        log.append(entry.get('date').strftime("%d.%m.%Y %H:%M") + ' ' + entry.get('event'))
    alert.update({'log': log})