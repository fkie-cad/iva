import unittest
from datetime import datetime
from pymongo import MongoClient
from local_repositories.tasks.task_info import TASKS_DB_COLLECTION
from tests.mock_config import *

TASK_NAME = 'update_db'
DATETIME_STR = '2016-12-21 10:04:07.769000'
FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DATETIME = datetime.strptime(DATETIME_STR, FORMAT)


class TestTaskDB(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.tasks_collection = self.test_db[TASKS_DB_COLLECTION]
        self.create_update_cve_search_db_obj()

    def create_update_cve_search_db_obj(self):
        self.task = patch_config_for('local_repositories.tasks.task_update_db', 'DailyUpdate')

    def test_create_task(self):
        self.task.create_task_in_db()

        # verify create task
        self.verify_new_created_task(self.tasks_collection.find_one({'name': TASK_NAME}))

    def test_task_is_not_created_if_exists(self):
        # mock create task
        self.tasks_collection.insert_one({'name': TASK_NAME})

        # try to create already created task
        self.task.create_task_in_db()

        # verify second task was not created
        self.assertEqual(1, len(list(self.tasks_collection.find({'name': TASK_NAME}))))

    def test_update_execution_time(self):
        # mock create task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00'})

        # update execution time
        new_time = '14:00:00'
        self.task.update_execution_time(new_time)

        # verify
        self.assertEqual(self.get_task().get('execution_time'), new_time)

    def test_execution_time_is_not_updated_with_wrong_time_format(self):
        # mock create task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00'})

        # update execution time with wrong format
        self.task.update_execution_time('1456')

        # verify time was not updated
        self.assertEqual(self.get_task().get('execution_time'), '00:00:00')

    def test_activate_task(self):
        # mock create task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'status': 'inactive'})

        # activate task
        self.task.activate_task()

        # verify
        self.assertEqual('active', self.get_task().get('status'))

    def test_deactivate_task(self):
        # mock create task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'next_execution': DATETIME, 'status': 'active'})

        # activate task
        self.task.deactivate_task()

        # verify
        task_dict = self.get_task()
        self.assertEqual('inactive', task_dict.get('status'))
        self.assertEqual('', task_dict.get('next_execution'))

    def test_activate_task_updates_next_execution(self):
        # mock create task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'status': 'inactive', 'next_execution': ''})

        # activate task
        self.task.activate_task()

        # verify
        self.assertEqual('active', self.get_task().get('status'))
        self.assertFalse('' == self.get_task().get('next_execution'))

    def test_get_task(self):
        # mock insert task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'status': 'inactive'})

        # get task
        task = self.task.get_task_info()

        # verify
        self.assertIsNotNone(task)

    def test_get_task_returns_none(self):
        # get task
        task = self.task.get_task_info()

        # verify
        self.assertIsNone(task)

    def test_update_task_next_execution(self):
        # mock insert task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'next_execution': ''})

        # update task's next execution
        self.task.update_next_execution(DATETIME)

        # verify
        self.assertEqual(DATETIME_STR, str(self.get_task().get('next_execution')))

    def test_update_task_last_execution(self):
        # mock insert task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'last_execution': ''})

        # update task's next execution
        now = datetime.now()
        self.task.update_last_execution(now)

        # verify
        self.assertEqual(now.date(), self.get_task().get('last_execution').date())
        self.assertEqual(now.hour, self.get_task().get('last_execution').hour)

    def test_is_task_active_returns_true(self):
        # mock insert task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'status': 'active'})

        self.assertTrue(self.task.is_task_active())

    def test_is_task_active_returns_false(self):
        # mock insert task
        self.tasks_collection.insert_one({'name': TASK_NAME, 'execution_time': '00:00:00', 'status': 'inactive'})

        self.assertFalse(self.task.is_task_active())

    def test_is_task_active_returns_false_when_task_does_not_exist_in_db(self):
        self.assertFalse(self.task.is_task_active())

    def verify_new_created_task(self, created_task):
        self.assertIsNotNone(created_task)
        self.assertEqual('inactive', created_task.get('status'))
        self.assertEqual('00:00:00', created_task.get('execution_time'))
        self.assertEqual('', created_task.get('last_execution'))
        self.assertEqual('', created_task.get('next_execution'))

    def get_task(self):
        return self.tasks_collection.find_one({'name': TASK_NAME})

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()

if __name__ == '__main__':
    unittest.main()
