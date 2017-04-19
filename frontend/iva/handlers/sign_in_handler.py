from django.http import HttpResponse
from django.template import loader

from user_authentication.user import User
from .request_handler_utils import *

USER_SESSION_KEY = 'user'
SIGN_IN_TEMPLATE = loader.get_template('iva/sign_in.html')
INDEX_TEMPLATE = loader.get_template('iva/index.html')


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

    def handle_request(self):
        if self.request.GET.get('sign_out') and USER_SESSION_KEY in self.request.session:
            del self.request.session[USER_SESSION_KEY]
            self.request.session.flush()

    def create_http_response(self):
        return HttpResponse(SIGN_IN_TEMPLATE.render({'is_valid_user': True}, self.request))


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.username = self.request.POST.get('username')
        self.pwd = self.request.POST.get('password')
        self.user = User()

    def handle_request(self):
        if self.user.verify_user(self.username, self.pwd):
            self.request.session[USER_SESSION_KEY] = self.user.username

    def create_http_response(self):
        if USER_SESSION_KEY in self.request.session:
            return HttpResponse(INDEX_TEMPLATE.render({}, self.request))
        return HttpResponse(SIGN_IN_TEMPLATE.render({'is_valid_user': False}, self.request))
