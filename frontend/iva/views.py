import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if not path in sys.path:
    sys.path.insert(1, path)

from .handlers import assign_cpe_handler
from .handlers import search_cves_handler
from .handlers import index_handler
from .handlers import new_software_handler
from .handlers import sw_products_with_cpe_handler
from .handlers import alerts_handler
from .handlers import cpe_wfn_handler
from .handlers import compare_cpe_handler
from .handlers import modify_cpe_handler
from .handlers import alert_log_handler
from .handlers import alert_notes_handler
from .handlers import alert_status_handler
from .handlers import cve_matches_handler
from .handlers import sign_in_handler
from .handlers.sign_in_handler import USER_SESSION_KEY
from .handlers import users_handler
from .handlers import add_user_handler
from .handlers import change_user_pwd_handler
from .handlers import modify_user_handler
from .handlers import daily_db_update_handler
from .handlers import change_daily_db_update_time_handler
from .handlers import grouped_cve_matches_handler


def sign_in(request):
    return sign_in_handler.handle_request(request)


def index(request):
    if USER_SESSION_KEY in request.session:
        return index_handler.handle_request(request)
    return sign_in(request)


def assign_cpe(request):
    if USER_SESSION_KEY in request.session:
        return assign_cpe_handler.handle_request(request)
    return sign_in(request)


def search_cves(request):
    if USER_SESSION_KEY in request.session:
        return search_cves_handler.handle_request(request)
    return sign_in(request)


def cve_matches(request):
    if USER_SESSION_KEY in request.session:
        return cve_matches_handler.handle_request(request)
    return sign_in(request)


def new_software(request):
    if USER_SESSION_KEY in request.session:
        return new_software_handler.handle_request(request)
    return sign_in(request)


def sw_products_with_cpe(request):
    if USER_SESSION_KEY in request.session:
        return sw_products_with_cpe_handler.handle_request(request)
    return sign_in(request)


def alerts(request):
    if USER_SESSION_KEY in request.session:
        return alerts_handler.handle_request(request)
    return sign_in(request)


def cpe_wfn(request):
    if USER_SESSION_KEY in request.session:
        return cpe_wfn_handler.handle_request(request)
    return sign_in(request)


def compare_cpe(request):
    if USER_SESSION_KEY in request.session:
        return compare_cpe_handler.handle_request(request)
    return sign_in(request)


def modify_cpe(request):
    if USER_SESSION_KEY in request.session:
        return modify_cpe_handler.handle_request(request)
    return sign_in(request)


def alert_log(request):
    if USER_SESSION_KEY in request.session:
        return alert_log_handler.handle_request(request)
    return sign_in(request)


def alert_notes(request):
    if USER_SESSION_KEY in request.session:
        return alert_notes_handler.handle_request(request)
    return sign_in(request)


def alert_status(request):
    if USER_SESSION_KEY in request.session:
        return alert_status_handler.handle_request(request)
    return sign_in(request)


def users(request):
    if USER_SESSION_KEY in request.session:
        return users_handler.handle_request(request)
    return sign_in(request)


def add_user(request):
    if USER_SESSION_KEY in request.session:
        return add_user_handler.handle_request(request)
    return sign_in(request)


def change_user_pwd(request):
    if USER_SESSION_KEY in request.session:
        return change_user_pwd_handler.handle_request(request)
    return sign_in(request)


def modify_user(request):
    if USER_SESSION_KEY in request.session:
        return modify_user_handler.handle_request(request)
    return sign_in(request)


def local_repositories(request):
    if USER_SESSION_KEY in request.session:
        return daily_db_update_handler.handle_request(request)
    return sign_in(request)


def change_daily_db_update_time(request):
    if USER_SESSION_KEY in request.session:
        return change_daily_db_update_time_handler.handle_request(request)
    return sign_in(request)


def grouped_cve_matches(request):
    if USER_SESSION_KEY in request.session:
        return grouped_cve_matches_handler.handle_request(request)
    return sign_in(request)