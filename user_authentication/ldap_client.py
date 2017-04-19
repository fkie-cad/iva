import ssl
import config
import traceback
import logger
from ldap3 import Server, Connection, Tls
from ldap3.core.exceptions import LDAPSocketOpenError, LDAPStartTLSError, LDAPPasswordIsMandatoryError


CONNECT_TIMEOUT = 15


def get_user_from_ldap_dir(username, password):
    user = None
    connection = create_connection(password, username)
    if connection:
        try:
            if connection.bind():
                user = connection.extend.standard.who_am_i()
            connection.unbind()
        except (LDAPPasswordIsMandatoryError, Exception):
            log_traceback()
    return user


def create_connection(password, username):
    try:
        connection = Connection(create_server(), get_bind_dn(username), password)
        connection.open()
        start_tls(connection)
        return connection
    except (LDAPSocketOpenError, LDAPStartTLSError, Exception):
        log_traceback()
        return False


def create_server():
    if config.is_ldap_tls_enabled():
        return Server(config.get_ldap_host(), port=config.get_ldap_port(), tls=create_tls_context(), connect_timeout=CONNECT_TIMEOUT)
    return Server(config.get_ldap_host(), port=config.get_ldap_port(), connect_timeout=CONNECT_TIMEOUT)


def create_tls_context():
    return Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2, ca_certs_file=config.get_ldap_cacert_file_path())


def get_bind_dn(username):
    return 'cn='+username+','+config.get_ldap_base_dn()


def start_tls(connection):
    if config.is_ldap_tls_enabled():
        connection.starttls()


def log_traceback():
    logger.error('LDAP - ' + str(traceback.format_exc()))