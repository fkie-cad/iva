from threading import Timer
from local_repositories.tasks import datetime_utils as time_utils


class TaskScheduler(object):

    class __SingletonTaskScheduler:

        def __init__(self):
            self.scheduled_tasks = {}
            self.running_tasks = []

        def schedule_task(self, task):
            if task.is_task_active():
                update_next_time_execution(task)
                timer = self.start_task_timer(task)
                self.scheduled_tasks.update({task.name: timer})

        def schedule_task_now(self, task):
            self.scheduled_tasks.update({task.name: self.start_task_now(task)})

        def start_task_timer(self, task):
            timer = Timer(get_task_timeout(task), self.execute_task, [task])
            timer.start()
            return timer

        def start_task_now(self, task):
            timer = Timer(1, self.execute_task_only_once, [task])
            timer.start()
            return timer

        def execute_task(self, task):
            self.execute_task_only_once(task)
            update_last_time_execution(task)
            self.reschedule_task(task)

        def execute_task_only_once(self, task):
            self.running_tasks.append(task.name)
            task.execute()
            self.running_tasks.remove(task.name)

        def reschedule_task(self, task):
            self.remove_task_from_scheduled_tasks_list(task)
            self.schedule_task(task)

        def is_task_scheduled(self, task_name):
            return task_name in self.scheduled_tasks

        def is_task_running(self, task_name):
            return task_name in self.running_tasks

        def cancel_task(self, task):
            if task.name in self.scheduled_tasks:
                timer = self.get_task_timer(task)
                timer.cancel()

        def get_number_of_scheduled_tasks(self):
            return len(self.scheduled_tasks)

        def remove_task_from_scheduled_tasks_list(self, task):
            if task.name in self.scheduled_tasks:
                del self.scheduled_tasks[task.name]

        def get_task_timer(self, task):
            return self.scheduled_tasks.get(task.name)

    __instance = None

    def __new__(cls):
        if not TaskScheduler.__instance:
            TaskScheduler.__instance = TaskScheduler.__SingletonTaskScheduler()
        return TaskScheduler.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)


def get_task_timeout(task):
    return time_utils.calculate_task_execution_timeout(task.get_execution_time())


def update_next_time_execution(task):
    task.update_next_execution(get_task_next_execution(task))


def get_task_next_execution(task):
    return time_utils.calculate_task_next_execution_datetime(task.get_execution_time())


def update_last_time_execution(task):
    task.update_last_execution(time_utils.get_current_datetime())

