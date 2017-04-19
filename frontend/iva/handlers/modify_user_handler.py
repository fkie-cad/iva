from django.http import HttpResponse
from django.template import loader

from user_authentication.user import User
from .request_handler_utils import *

TEMPLATE = loader.get_template('iva/modify_user.html')
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
        self.surname = self.request.GET.get('surname')
        self.name = self.request.GET.get('name')
        self.user = User()

    def handle_request(self):
        if self.request.GET.get('option') == 'check_user':
            if self.user.exist_user_with_username(self.username):
                return HttpResponse({'exist'}, self.request)
            return HttpResponse({'not_exist'}, self.request)
        return HttpResponse(TEMPLATE.render({'old_username': self.username,
                                             'name': self.name,
                                             'surname': self.surname}, self.request))


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.old_username = self.request.POST.get('old_username')
        self.username = self.request.POST.get('username')
        self.surname = self.request.POST.get('surname')
        self.name = self.request.POST.get('name')
        self.user = User()

    def handle_request(self):
        self.user.modify_user(self.old_username, self.username, self.name, self.surname)
        return HttpResponse('<script type="text/javascript">window.close(); '
                            'window.opener.parent.location.href = "/iva/users.html";</script>')

