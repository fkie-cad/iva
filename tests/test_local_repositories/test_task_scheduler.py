import time
import unittest
from pymongo import MongoClient
from tests.mock_config import *
from local_repositories.tasks.scheduler import TaskScheduler
from local_repositories.tasks.task_info import TASKS_DB_COLLECTION, TaskInfo

TIMEOUT_FUNCTION = 'local_repositories.tasks.scheduler.time_utils.calculate_task_execution_timeout'
TASK_CLASS = 'local_repositories.tasks.scheduler.Task'


class TestTaskScheduler(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.tasks_collection = self.test_db[TASKS_DB_COLLECTION]
        self.create_task_object()

    def create_task_object(self):
        self.task = patch_config_for('tests.test_local_repositories.test_task_scheduler', 'MockTask')

    def test_task_scheduler_is_singleton_class(self):
        self.assertEqual(id(TaskScheduler()), id(TaskScheduler()))

    def test_schedule_task(self):
        self.task.create_task_in_db()
        self.task.activate_task()
        self.next_execution = self.task.get_task_info().get('next_execution')
        self.last_execution = self.task.get_task_info().get('last_execution')

        with patch(TIMEOUT_FUNCTION, return_value=2):
            scheduler = TaskScheduler()
            scheduler.schedule_task(self.task)
            self.assertTrue(scheduler.is_task_scheduled(self.task.name))
            self.assertFalse(self.next_execution == self.task.get_task_info().get('next_execution'))
            # task was scheduled, every 2 seconds it is executed
            time.sleep(3)
            self.assertEqual(1, self.task.execution_calls)
            self.assertFalse(self.last_execution == self.task.get_task_info().get('last_execution'))
            self.last_execution = self.task.get_task_info().get('last_execution')

            time.sleep(2)
            self.assertEqual(2, self.task.execution_calls)
            self.assertFalse(self.last_execution == self.task.get_task_info().get('last_execution'))

            # we deactivate the task in order to stop the execution of the task
            # since the task is inactive, it must not be scheduled
            self.task.deactivate_task()
            time.sleep(2)
            self.assertFalse(scheduler.is_task_scheduled(self.task.name))

    def test_task_is_not_scheduled_if_it_is_inactive(self):
        self.task.create_task_in_db()
        scheduler = TaskScheduler()
        scheduler.schedule_task(self.task)

        self.assertEqual(0, self.task.execution_calls)
        self.assertFalse(scheduler.is_task_scheduled(self.task.name))

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()

if __name__ == '__main__':
    unittest.main()


class MockTask(TaskInfo):

    def __init__(self):
        super().__init__()
        self.name = 'update_db'
        self.execution_calls = 0

    def execute(self):
        self.execution_calls += 1
