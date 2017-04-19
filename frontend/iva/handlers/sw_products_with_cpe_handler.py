from django.http import HttpResponse
from django.template import loader
from inventory.software_cpe import SoftwareCPE
from inventory.inventory import Inventory
from .request_handler_utils import *

template = loader.get_template('iva/sw_products_with_cpe.html')


def handle_request(request):
    if is_get_request(request):
        get_handler = GetHandler(request)
        return get_handler.create_http_response()


class GetHandler:
    def __init__(self, request):
        self.cpe_inventory = SoftwareCPE()
        self.request = request
        self.inventory = Inventory()

    def create_http_response(self):
        context = self.create_context()
        return HttpResponse(template.render(context, self.request))

    def create_context(self):
        return {'inventory': self.inventory.get_software_products_with_assigned_cpe()}
