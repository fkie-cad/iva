from local_repositories.tasks.task_info import TaskInfo
from local_repositories.tasks import operations


class DailyUpdate(TaskInfo):

    def __init__(self):
        super().__init__()
        self.name = 'update_db'

    def execute(self):
        operations.update_db()
