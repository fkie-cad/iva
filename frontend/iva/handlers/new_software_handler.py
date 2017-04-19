from django.http import HttpResponse
from django.template import loader
from .request_handler_utils import *
from inventory.inventory import Inventory

template = loader.get_template('iva/new_software.html')


def handle_request(request):
    handler = get_handler(request)
    response = handler.handle_request()
    return response


def get_handler(request):
    if is_get_request(request):
        return GetHandler(request)
    return PostHandler(request)


class GetHandler:

    def __init__(self, request):
        self.inventory = Inventory()
        self.request = request
        self.option = self.request.GET.get('option')
        self.read_inventory_error = False

    def handle_request(self):
        self.handle_get_options()
        return self.create_http_response()

    def handle_get_options(self):
        if self.option == 'read_inventory':
            self.read_inventory()

    def create_http_response(self):
        return HttpResponse(self.render_template())

    def read_inventory(self):
        try:
            self.inventory.insert_new_software_products_to_db()
        except:
            self.read_inventory_error = True

    def render_template(self):
        return template.render(self.create_context(), self.request)

    def create_context(self):
        return {'items': self.get_new_software(), 'read_inventory_error': self.read_inventory_error}

    def get_new_software(self):
        return self.inventory.get_software_products_without_assigned_cpe()


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.inventory = Inventory()
        self.product_to_search = self.request.POST.get('product_to_search')

    def handle_request(self):
        software_list = self.get_new_software()
        req_context = create_context(software_list)
        req_template = self.create_template(req_context)
        return create_http_response(req_template)

    def create_template(self, req_context):
        return template.render(req_context, self.request)

    def get_new_software(self):
        return self.inventory.search_software_products_without_assigned_cpe(self.product_to_search)


def create_context(new_software_list):
    return {'items': new_software_list, 'read_inventory_error': False}


def create_http_response(template_):
    return HttpResponse(template_)