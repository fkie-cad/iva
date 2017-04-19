from unittest.mock import patch
import importlib

DB_HOST = 'localhost'
DB_PORT = 27017
IVA_DB_NAME = 'test_iva_db'
CVE_SEARCH_DB_NAME = 'test_cve_search_db'


def path_db_host():
    return patch('config.get_database_host', return_value=DB_HOST)


def path_db_port():
    return patch('config.get_database_port', return_value=DB_PORT)


def path_db_name():
    return patch('config.get_database_name', return_value=IVA_DB_NAME)


def path_cve_search_db_name():
    return patch('config.get_cve_search_db_name', return_value=CVE_SEARCH_DB_NAME)


def path_db_auth_enabled():
    return patch('config.is_database_authentication_enabled', return_value=False)


def patch_config_for(module_name=None, class_name=None):
    with path_db_host():
        with path_db_port():
            with path_db_name():
                with path_db_auth_enabled():
                    with path_cve_search_db_name():
                        module = importlib.import_module(module_name)
                        class_ = getattr(module, class_name)
                        return class_()
