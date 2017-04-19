from django.http import HttpResponse
from django.template import loader

from user_authentication.user import User
from .request_handler_utils import *

TEMPLATE = loader.get_template('iva/change_user_pwd.html')
USERS_TEMPLATE = loader.get_template('iva/users.html')


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
        self.username = self.request.GET.get('username')

    def handle_request(self):
        return HttpResponse(TEMPLATE.render({'username': self.username}, self.request))


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.username = self.request.POST.get('username')
        self.old_pwd = self.request.POST.get('old_pwd')
        self.new_pwd = self.request.POST.get('new_pwd')
        self.user = User()

    def handle_request(self):
        if self.request.POST.get('verify_old_pwd'):
            if self.user.exists_in_db(self.username, self.old_pwd):
                return HttpResponse(True, self.request)
            return HttpResponse(False, self.request)
        else:
            pwd_changed = self.user.change_password(self.username, self.old_pwd, self.new_pwd)
            if pwd_changed:
                return HttpResponse('<script type="text/javascript">window.close(); '
                                    'window.opener.parent.location.href = "/iva/users.html?option=pwd_changed&username='+self.username+'";</script>')
            return HttpResponse(TEMPLATE.render({'username': self.username, 'error': True}, self.request))

