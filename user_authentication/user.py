import os
import logger
from database import Database
from user_authentication import ldap_client
from user_authentication.user_dict import *
from utils import generate_password

DUMMY_CREDENTIALS_FILE = 'dummy_user_credentials.txt'
USER_DB_COLLECTION = 'users'
USER_TYPES = namedtuple('User_Types', ['LOCAL', 'LDAP'])('local', 'ldap')


class User:

    def __init__(self):
        self.db = Database()
        self.username = None
        self.user_type = None

    def insert_new_user(self, name, surname, username, pwd):
        if not self.exists_in_db(username, pwd):
            user_dict = create_user_dict(name, pwd, surname, username)
            self.db.insert_document_in_collection(user_dict, USER_DB_COLLECTION)
        else:
            raise UserExistsException(username)

    def verify_user(self, username, pwd):
        if self.exists_in_db(username, pwd):
            self.set_user_info(username, USER_TYPES.LOCAL)
            log_user_authenticated(username)
            return True
        elif is_ldap_user(pwd, username):
            self.set_user_info(username, USER_TYPES.LDAP)
            log_user_authenticated(username)
            return True
        log_invalid_user(username)
        return False

    def set_user_info(self, username, user_type):
        self.username = username
        self.user_type = user_type

    def exists_in_db(self, username, pwd):
        return self.db.exist_doc_in_collection(get_username_pwd_dict(pwd, username), USER_DB_COLLECTION)

    def exist_user_with_username(self, username):
        return self.db.exist_doc_in_collection(get_username_dict(username), USER_DB_COLLECTION)

    def get_user_from_db(self, username, pwd):
        return self.db.search_document_in_collection(get_username_pwd_dict(pwd, username), USER_DB_COLLECTION)

    def get_users(self):
        return list(self.db.get_documents_from_collection(USER_DB_COLLECTION))

    def delete_user(self, username):
        self.db.delete_document_from_collection(get_username_dict(username), USER_DB_COLLECTION)

    def change_password(self, username, old_pwd, new_pwd):
        if self.exists_in_db(username, old_pwd):
            if new_pwd != '' or new_pwd is not None:
                self.db.update_document_in_collection(get_username_dict(username), get_pwd_dict(new_pwd), USER_DB_COLLECTION)
                return True
        return False

    def modify_user(self, old_username, new_username, name, surname):
        if old_username != new_username:
            if not self.username_exists(new_username):
                self.modify(old_username, new_username, name, surname)
        else:
            self.modify(old_username, new_username, name, surname)

    def modify(self, old_username, new_username, name, surname):
        self.db.update_document_in_collection(get_username_dict(old_username),
                                              get_name_surname_username_dict(name, new_username, surname),
                                              USER_DB_COLLECTION)

    def username_exists(self, username):
        return self.db.exist_doc_in_collection(get_username_dict(username), USER_DB_COLLECTION)

    def is_user_collection_empty(self):
        return self.db.get_number_of_documents_in_collection(USER_DB_COLLECTION) == 0

    def create_dummy_user(self):
        username = generate_password()
        password = generate_password()
        self.insert_dummy_user_in_db(username, password)
        print_credentials_on_terminal(username, password)
        create_dummy_user_file(username, password)

    def insert_dummy_user_in_db(self, username, password):
        self.insert_new_user('Dummy', 'User', username, password)


def is_ldap_user(pwd, username):
    ldap_user = ldap_client.get_user_from_ldap_dir(username, pwd)
    if ldap_user is not None:
        return True
    return False


def create_dummy_user_file(username, password):
    f = open(get_dummy_user_file(), 'wb+')
    f.write(bytes(username + '\n', 'UTF-8'))
    f.write(bytes(password + '\n', 'UTF-8'))
    f.close()


def get_dummy_user_file():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), DUMMY_CREDENTIALS_FILE)


def print_credentials_on_terminal(username, password):
    print('################ Dummy User Credentials ################')
    print('username: ' + str(username))
    print('password: ' + str(password))
    print('########################################################')


def log_user_authenticated(username):
    logger.info('USER - ' + str(username) + ' authenticated successfully')


def log_invalid_user(username):
    logger.error('USER - failed to authenticate user ' + str(username))


class UserExistsException(Exception):

    def __init__(self, value):
        self.user = value

    def __str__(self):
        return repr(self.user)



