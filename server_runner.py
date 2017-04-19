import os
import threading
import config
import logger

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
MANAGE_FILE = ROOT_DIR + '/frontend/manage.py'
INDEX_FILE = 'web/index.py'


def run_iva_server(config_file):
    logger.info("starting HTTP server for IVA")
    IvaHttpServerThread(config_file).start()


def run_cve_search_server():
    logger.info("starting HTTP server for cve-search")
    if is_cve_search_installed():
        CveSearchHttpServerThread().start()
    else:
        logger.error("cve-search was not found in " + config.get_cve_search_dir())


def is_cve_search_installed():
    return os.path.exists(get_cve_search_index_file())


class IvaHttpServerThread(threading.Thread):

    def __init__(self, config_file):
        threading.Thread.__init__(self)
        self.config_file = config_file

    def run(self):
        os.system('python3 ' + MANAGE_FILE + ' runserver ' + get_iva_server_address() + ' ' + self.config_file)


def get_iva_server_address():
    return config.get_frontend_host() + ':' + config.get_frontend_port()


class CveSearchHttpServerThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        os.system('python3 ' + get_cve_search_index_file())


def get_cve_search_index_file():
        return os.path.join(config.get_cve_search_dir(), INDEX_FILE)