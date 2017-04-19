import hashlib
from collections import namedtuple

DICT_KEYS = namedtuple('DICT_KEYS', ['NAME', 'SURNAME', 'USERNAME', 'PWD_HASH'])('name', 'surname', 'username', 'pwd_sha512')


def create_user_dict(name, pwd, surname, username):
    return {DICT_KEYS.NAME: name, DICT_KEYS.SURNAME: surname, DICT_KEYS.USERNAME: username, DICT_KEYS.PWD_HASH: hash_(pwd)}


def get_username_pwd_dict(pwd, username):
    return {DICT_KEYS.USERNAME: username, DICT_KEYS.PWD_HASH: hash_(pwd)}


def get_username_dict(username):
    return {DICT_KEYS.USERNAME: username}


def get_pwd_dict(new_pwd):
    return {DICT_KEYS.PWD_HASH: hash_(new_pwd)}


def get_name_surname_username_dict(name, new_username, surname):
    return {DICT_KEYS.NAME: name, DICT_KEYS.SURNAME: surname, DICT_KEYS.USERNAME: new_username}


def hash_(pwd):
    return hashlib.sha512(str.encode(pwd)).hexdigest()
