from django.http import HttpResponse
from local_repositories.tasks.task_update_db import DailyUpdate
from local_repositories.tasks.scheduler import TaskScheduler
from .request_handler_utils import *
from django.template import loader


TEMPLATE = loader.get_template('iva/change_daily_db_update_time.html')


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
        self.task_name = self.request.GET.get('name')
        self.current_hour = self.request.GET.get('hour')
        self.current_minute = self.request.GET.get('minute')

    def handle_request(self):
        return HttpResponse(TEMPLATE.render({'task_name': self.task_name,
                                             'range_hour': range(24),
                                             'range_minute': range(60),
                                             'current_hour': self.current_hour,
                                             'current_minute': self.current_minute}, self.request))


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.daily_db_update = DailyUpdate()
        self.hour = self.request.POST.get('execution_time_hour')
        self.minute = self.request.POST.get('execution_time_minute')
        self.task_name = self.request.POST.get('task_name')
        self.task_scheduler = TaskScheduler()

    def handle_request(self):
        self.daily_db_update.update_execution_time(self.get_time())
        self.task_scheduler.cancel_task(self.daily_db_update)
        self.task_scheduler.reschedule_task(self.daily_db_update)
        return HttpResponse('<script type="text/javascript">window.close(); '
                            'window.opener.parent.location.href = "/iva/local_repositories.html";</script>')

    def get_time(self):
        return self.hour + ':' + self.minute + ':' + '00'
