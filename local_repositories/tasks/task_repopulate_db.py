from local_repositories.tasks import operations


class RepopulateDB:

    def __init__(self):
        self.name = 'repopulate_db'

    def execute(self):
        operations.repopulate_db()
        operations.update_iva_db()