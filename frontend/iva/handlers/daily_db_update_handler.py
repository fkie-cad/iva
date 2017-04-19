from django.http import HttpResponse
from local_repositories.tasks.task_update_db import DailyUpdate
from local_repositories.tasks.task_populate_db import PopulateDB
from local_repositories.tasks.task_repopulate_db import RepopulateDB
from local_repositories.tasks.scheduler import TaskScheduler
from local_repositories.cve_search import CVESearchDB
from local_repositories.cpe_dict import CPEDict
from local_repositories.cve_feeds import CVEFeeds
from .request_handler_utils import *
from django.template import loader
import time

TEMPLATE = loader.get_template('iva/local_repositories.html')


def handle_request(request):
    handler = get_handler(request)
    handler.handle_request()
    return handler.create_http_response()


def get_handler(request):
    if is_get_request(request):
        return GetHandler(request)
    return PostHandler(request)


def add_execution_hour(task):
    execution_time = str(task.get('execution_time')).split(':')
    task.update({'execution_hour': execution_time[0]})


def add_execution_minute(task):
    execution_time = str(task.get('execution_time')).split(':')
    task.update({'execution_minute': execution_time[1]})


class GetHandler:

    def __init__(self, request):
        self.request = request
        self.daily_db_update = DailyUpdate()
        self.cve_search_db = CVESearchDB()
        self.task_scheduler = TaskScheduler()
        self.option = self.request.GET.get('option')
        self.task_name = self.request.GET.get('name')
        self.cpe_dict = CPEDict()
        self.cve_feeds = CVEFeeds()

    def handle_request(self):
        self.daily_db_update.create_task_in_db()
        if not self.task_scheduler.is_task_scheduled(self.daily_db_update.name):
            self.task_scheduler.schedule_task(self.daily_db_update)

    def create_http_response(self):
        return HttpResponse(TEMPLATE.render({'task': self.get_task_info(),
                                             'db_populated': self.is_db_populated(),
                                             'cve_search_cpe_entries': self.cve_search_db.get_number_of_cpes_entries(),
                                             'cve_search_cve_entries': self.cve_search_db.get_number_of_cves_entries(),
                                             'iva_cpe_entries': self.cpe_dict.number_of_entries(),
                                             'iva_cve_entries': self.cve_feeds.number_of_entries(),
                                             'is_population_running': self.is_db_population_running(),
                                             'is_repopulation_running': self.is_db_repopulation_running()},
                                            self.request))

    def is_db_populated(self):
        if not self.is_db_population_running():
            return self.cve_search_db.is_cve_search_populated()
        return False

    def is_db_population_running(self):
        return self.task_scheduler.is_task_running('populate_db')

    def is_db_repopulation_running(self):
        return self.task_scheduler.is_task_running('repopulate_db')

    def get_task_info(self):
        task_info = self.daily_db_update.get_task_info()
        add_execution_hour(task_info)
        add_execution_minute(task_info)
        self.add_is_scheduled(task_info)
        self.add_is_running(task_info)
        return task_info

    def add_is_scheduled(self, task_info):
        if self.task_scheduler.is_task_scheduled(task_info.get('name')):
            task_info.update({'is_scheduled': 'Yes'})
        else:
            task_info.update({'is_scheduled': 'No'})

    def add_is_running(self, task_info):
        if self.task_scheduler.is_task_running(task_info.get('name')):
            task_info.update({'is_running': 'Yes'})
        else:
            task_info.update({'is_running': 'No'})


class PostHandler:

    def __init__(self, request):
        self.request = request
        self.daily_db_update = DailyUpdate()
        self.task_scheduler = TaskScheduler()
        self.option = self.request.POST.get('option')
        self.task_name = self.request.POST.get('name')

    def handle_request(self):
        if self.option == 'activate':
            self.daily_db_update.activate_task()
        elif self.option == 'deactivate':
            self.daily_db_update.deactivate_task()
            self.task_scheduler.cancel_task(self.daily_db_update)
            self.task_scheduler.reschedule_task(self.daily_db_update)
        elif self.option == 'populate_db':
            self.task_scheduler.schedule_task_now(PopulateDB())
            time.sleep(1)
        elif self.option == 'repopulate_db':
            self.task_scheduler.schedule_task_now(RepopulateDB())
            time.sleep(1)

    def create_http_response(self):
        return HttpResponse('')
