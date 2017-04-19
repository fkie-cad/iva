from collections import namedtuple
from database import Database
from local_repositories.tasks import datetime_utils


TASKS_DB_COLLECTION = 'tasks'
DEFAULT_EXECUTION_TIME = '00:00:00'
STATUS = namedtuple('Status', ['active', 'inactive'])('active', 'inactive')
TASK = namedtuple('DictKeys', ['name', 'status', 'execution_time', 'next_execution', 'last_execution'])\
                                       ('name', 'status', 'execution_time', 'next_execution', 'last_execution')


class TaskInfo:

    def __init__(self):
        self.name = None
        self.db = Database()

    def create_task_in_db(self):
        if not self.task_exists_in_db():
            self.db.insert_document_in_collection(create_task_dict(self.name), TASKS_DB_COLLECTION)

    def task_exists_in_db(self):
        return self.db.exist_doc_in_collection({TASK.name: self.name}, TASKS_DB_COLLECTION)

    def update_execution_time(self, new_time):
        if datetime_utils.verify_time_format(new_time):
            self.db.update_document_in_collection({TASK.name: self.name}, {TASK.execution_time: new_time},
                                                  TASKS_DB_COLLECTION)
            self.update_next_execution(self.get_next_execution_datetime())

    def activate_task(self):
        self.update_next_execution(self.get_next_execution_datetime())
        self.db.update_document_in_collection({TASK.name: self.name}, {TASK.status: STATUS.active},
                                              TASKS_DB_COLLECTION)

    def deactivate_task(self):
        self.update_next_execution('')
        self.db.update_document_in_collection({TASK.name: self.name}, {TASK.status: STATUS.inactive},
                                              TASKS_DB_COLLECTION)

    def get_next_execution_datetime(self):
        return datetime_utils.calculate_task_next_execution_datetime(self.get_task_info().get(TASK.execution_time))

    def update_next_execution(self, datetime_):
        self.db.update_document_in_collection({TASK.name: self.name}, {TASK.next_execution: datetime_},
                                              TASKS_DB_COLLECTION)

    def update_last_execution(self, datetime_):
        self.db.update_document_in_collection({TASK.name: self.name}, {TASK.last_execution: datetime_},
                                              TASKS_DB_COLLECTION)

    def get_task_info(self):
        return self.db.search_document_in_collection({TASK.name: self.name}, TASKS_DB_COLLECTION)

    def get_execution_time(self):
        task_info = self.get_task_info()
        return task_info.get(TASK.execution_time)

    def is_task_active(self):
        return self.db.exist_doc_in_collection({TASK.name: self.name, TASK.status: STATUS.active}, TASKS_DB_COLLECTION)


def create_task_dict(task_name):
    return {TASK.name: task_name, TASK.status: STATUS.inactive,
            TASK.execution_time: DEFAULT_EXECUTION_TIME, TASK.last_execution: '', TASK.next_execution: ''}