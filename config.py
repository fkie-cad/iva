from urllib.parse import urljoin
import configparser
import os
import logger

config_parser = None


def load_configuration_from_file(file_path):
    global config_parser
    if config_parser is None:
        if os.path.exists(file_path):
            config_parser = configparser.ConfigParser()
            config_parser.read(file_path)
            logger.info('configuration file was read from ' + file_path)
        else:
            logger.info('unable to read configuration file: ' + file_path)


def reload_configuration(file_path):
    global config_parser
    config_parser = None
    load_configuration_from_file(file_path)


def get_database_host():
    return config_parser.get('database', 'host')


def get_database_port():
    return config_parser.getint('database', 'port')


def get_database_name():
    return config_parser.get('database', 'name')


def get_database_user():
    return config_parser.get('database', 'user')


def get_database_password():
    return config_parser.get('database', 'password')


def is_database_authentication_enabled():
    try:
        return config_parser.getboolean('database', 'authentication')
    except ValueError:
        return False


def get_cve_search_db_name():
    return config_parser.get('cve-search', 'db')


def get_cve_search_dir():
    return config_parser.get('cve-search', 'dir')


def get_cve_search_url():
    return add_path_to_cve_search_url(config_parser.get('cve-search', 'url'))


def add_path_to_cve_search_url(url):
    return urljoin(url, '/cve/')


def get_log_file():
    return config_parser.get('logging', 'file')


def get_frontend_host():
    return config_parser.get('frontend', 'host')


def get_frontend_port():
    return config_parser.get('frontend', 'port')


def get_inventory_database_host():
    return config_parser.get('inventory-database', 'host')


def get_inventory_database_user():
    return config_parser.get('inventory-database', 'user')


def get_inventory_database_password():
    return config_parser.get('inventory-database', 'password')


def get_glpi_db_name():
    return config_parser.get('inventory-database', 'name')


def get_smtp_server_host():
    return config_parser.get('smtp', 'host')


def get_smtp_server_port():
    return config_parser.get('smtp', 'port')


def get_smtp_user():
    return config_parser.get('smtp', 'user')


def get_smtp_password():
    return config_parser.get('smtp', 'password')


def get_smtp_sender():
    return config_parser.get('smtp', 'sender')


def get_smtp_receiver():
    return config_parser.get('smtp', 'receiver')


def is_smtp_starttls_enabled():
    try:
        return config_parser.getboolean('smtp', 'starttls')
    except ValueError:
        return False


def is_smtps_enabled():
    try:
        return config_parser.getboolean('smtp', 'smtps')
    except ValueError:
        return False


def is_verify_smtp_server_cert_enabled():
    try:
        return config_parser.getboolean('smtp', 'verify_server_cert')
    except ValueError:
        return False


def get_smtp_ca_cert_file():
    return config_parser.get('smtp', 'ca_cert_file')


def is_gpg_encryption_enabled():
    try:
        return config_parser.getboolean('gpg', 'required')
    except ValueError:
        return False


def get_gpg_home_dir():
    return config_parser.get('gpg', 'home_dir')


def get_gpg_pub_key_file():
    return config_parser.get('gpg', 'pub_key_file')


def get_ldap_host():
    return config_parser.get('ldap', 'host')


def get_ldap_port():
    return config_parser.getint('ldap', 'port')


def get_ldap_base_dn():
    return config_parser.get('ldap', 'base_dn')


def get_ldap_cacert_file_path():
    return config_parser.get('ldap', 'cacert')


def is_ldap_tls_enabled():
    try:
        return config_parser.getboolean('ldap', 'tls')
    except ValueError:
        return False
