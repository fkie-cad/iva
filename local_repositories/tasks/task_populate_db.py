from local_repositories.tasks import operations


class PopulateDB:

    def __init__(self):
        self.name = 'populate_db'

    def execute(self):
        operations.populate_db()
        operations.update_iva_db()
