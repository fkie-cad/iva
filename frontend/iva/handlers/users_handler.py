from django.http import HttpResponse
from django.template import loader

from user_authentication.user import User
from .request_handler_utils import *

TEMPLATE = loader.get_template('iva/users.html')


def handle_request(request):
    handler = get_handler(request)
    handler.handle_request()
    return handler.create_http_response()


def get_handler(request):
    if is_get_request(request):
        return GetHandler(request)
    return PostHandler(request)


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.option = self.request.GET.get('option')
        self.username = self.request.GET.get('username')
        self.user = User()

    def handle_request(self):
        pass

    def create_http_response(self):
        if self.option == 'pwd_changed':
            return HttpResponse(TEMPLATE.render(self.get_context_dict(), self.request))
        return HttpResponse(TEMPLATE.render({'users': self.user.get_users()}, self.request))

    def get_context_dict(self):
        return {'users': self.user.get_users(), 'pwd_changed': True, 'username': self.username}


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.option = self.request.POST.get('option')
        self.username = self.request.POST.get('username')
        self.user = User()

    def handle_request(self):
        if self.option == 'delete':
            self.user.delete_user(self.username)

    def create_http_response(self):
        return HttpResponse('OK')
