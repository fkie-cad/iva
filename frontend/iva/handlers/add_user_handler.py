from django.http import HttpResponse
from django.template import loader

from user_authentication.user import User
from .request_handler_utils import *

TEMPLATE = loader.get_template('iva/add_user.html')
TEMPLATE_USERS = loader.get_template('iva/users.html')


def handle_request(request):
    handler = get_handler(request)
    http_response = handler.handle_request()
    return http_response


def get_handler(request):
    if is_get_request(request):
        return GetHandler(request)
    return PostHandler(request)


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.context = {}
        self.user = User()

    def handle_request(self):
        if self.request.GET.get('option') == 'check_user':
            if self.user.exist_user_with_username(self.request.GET.get('username')):
                return HttpResponse({'exist'}, self.request)
            return HttpResponse({'not_exist': False}, self.request)
        return HttpResponse(TEMPLATE.render({}, self.request))


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.name = self.request.POST.get('name')
        self.surname = self.request.POST.get('surname')
        self.username = self.request.POST.get('username')
        self.pwd = self.request.POST.get('password')
        self.user = User()

    def handle_request(self):
        self.user.insert_new_user(self.name, self.surname, self.username, self.pwd)
        return HttpResponse(TEMPLATE_USERS.render({'users': self.user.get_users()}, self.request))
