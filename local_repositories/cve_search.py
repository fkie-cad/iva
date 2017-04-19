import os
import config
from database import Database

DOWNLOADER_FILE = 'sbin/db_mgmt.py'
CPE_DICT_DOWNLOADER_FILE = 'sbin/db_mgmt_cpe_dictionary.py'
UPDATER_FILE = 'sbin/db_updater.py'
CVE_SEARCH_CPE_COLLECTION = 'cpe'
CVE_SEARCH_CVE_COLLECTION = 'cves'


class CVESearchDB:

    def __init__(self):
        self.cve_search_db = Database(config.get_cve_search_db_name())

    def get_cpe_dict(self):
        return self.cve_search_db.get_documents_from_collection(CVE_SEARCH_CPE_COLLECTION)

    def get_cve_feeds(self, skip=0, limit=0):
        return self.cve_search_db.get_documents_from_collection_in_range(CVE_SEARCH_CVE_COLLECTION, skip, limit)

    def get_number_of_cves_entries(self):
        return self.cve_search_db.get_number_of_documents_in_collection(CVE_SEARCH_CVE_COLLECTION)

    def get_number_of_cpes_entries(self):
        return self.cve_search_db.get_number_of_documents_in_collection(CVE_SEARCH_CPE_COLLECTION)

    def is_cve_search_populated(self):
        return self.get_number_of_cpes_entries() > 0 and self.get_number_of_cves_entries() > 0

    def close(self):
        self.cve_search_db.close()


def populate_db():
    execute_file(get_downloader_file() + ' -p')
    execute_file(get_cpe_dict_downloader_file())


def update_db():
    execute_file(get_updater_file() + ' -c')


def repopulate_db():
    execute_file(get_updater_file() + ' -v -f')


def execute_file(file_):
    os.system('python3 ' + file_)


def get_downloader_file():
    return join_(DOWNLOADER_FILE)


def get_cpe_dict_downloader_file():
    return join_(CPE_DICT_DOWNLOADER_FILE)


def get_updater_file():
    return join_(UPDATER_FILE)


def join_(file_):
    return os.path.join(config.get_cve_search_dir(), file_)
