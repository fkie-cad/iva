from django.http import HttpResponse
from django.template import loader
from inventory.software_cve_matches import CVEMatches
from inventory.inventory import Inventory
from .request_handler_utils import *
from config import get_cve_search_url

template = loader.get_template('iva/cve_matches.html')


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

    def handle_post_request(self):
        if self.option == 'remove_cve':
            self.cve_matches.set_cve_match_as_removed(self.software_id, self.cve_id)
        elif self.option == 'restore_cve':
            self.cve_matches.restore_cve_match(self.software_id, self.cve_id)
        elif self.option == 'set_cve_as_positive':
            self.cve_matches.set_cve_match_as_positive(self.software_id, self.cve_id)
        elif self.option == 'set_cve_as_negative':
            self.cve_matches.set_cve_match_as_negative(self.software_id, self.cve_id)
        return HttpResponse('ok')

    def post_value(self, key):
        return self.request.POST.get(key)


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.cve_matches = CVEMatches()
        self.inventory = Inventory()
        self.option = self.get_value('option')
        self.vendor = self.get_value('vendor')
        self.product = self.get_value('product')
        self.vendors = self.get_vendors()
        self.products = []

    def get_vendors(self):
        vendors = self.inventory.get_vendors()
        vendors.append('all')
        return vendors

    def handle_get_request(self):
        pass

    def create_http_response(self):
        return HttpResponse(template.render(self.create_context(), self.request))

    def create_context(self):
        if self.option == 'show_removed':
            if self.vendor == 'all':
                return self.get_context_dict(['show_removed'], False)
            return self.get_context_dict(['show_removed'], True)
        elif self.option == 'hide_removed':
            if self.vendor == 'all':
                return self.get_context_dict(['hide_removed'], False)
            return self.get_context_dict(['hide_removed'], True)
        elif self.option == 'ordered_by_year_desc_hide_removed':
            if self.vendor == 'all':
                return self.get_context_dict(['ordered_by_year_desc', 'hide_removed'], False)
            return self.get_context_dict(['ordered_by_year_desc', 'hide_removed'], True)
        elif self.option == 'ordered_by_year_desc_show_removed':
            if self.vendor == 'all':
                return self.get_context_dict(['ordered_by_year_desc', 'show_removed'], False)
            return self.get_context_dict(['ordered_by_year_desc', 'show_removed'], True)
        elif self.option == 'ordered_by_year_asc_hide_removed':
            if self.vendor == 'all':
                return self.get_context_dict(['ordered_by_year_asc', 'hide_removed'], False)
            return self.get_context_dict(['ordered_by_year_asc', 'hide_removed'], True)
        elif self.option == 'ordered_by_year_asc_show_removed':
            if self.vendor == 'all':
                return self.get_context_dict(['ordered_by_year_asc', 'show_removed'], False)
            return self.get_context_dict(['ordered_by_year_asc', 'show_removed'], True)
        elif self.option == 'show_vendor_cves':
            return self.get_context_dict(['hide_removed'], True)
        return self.get_context_dict(['hide_removed'], False)

    def get_context_dict(self, filters, vendor_cves):
        if vendor_cves:
            cve_matches = self.cve_matches.get_vendor_product_cve_matches(self.vendor, self.product, filters)
            vendor = self.vendor
            product = self.product
            products = self.inventory.get_vendor_products(self.vendor)
        else:
            cve_matches = self.cve_matches.get_cve_matches(filters)
            vendor = 'all'
            product = 'all'
            products = self.products
        return {'cve_matches': cve_matches, 'vendors': self.vendors, 'products': products, 'vendor': vendor,
                'product': product, 'cve_search_url': get_cve_search_url()}

    def get_value(self, key):
        return self.request.GET.get(key)
