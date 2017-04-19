import hashlib
import unittest

from pymongo import MongoClient

from tests.mock_config import *
from user_authentication.user import USER_DB_COLLECTION, USER_TYPES, UserExistsException

NAME = 'test user'
SURNAME = 'test user surname'
USERNAME = 'admin'
PASSWORD = '123'


def get_hash_value(input_):
    return hashlib.sha512(str.encode(input_)).hexdigest()


PWD_SHA512 = get_hash_value(PASSWORD)


class TestUser(unittest.TestCase):

    def setUp(self):
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.db = self.mongodb_client[IVA_DB_NAME]
        self.user_collection = self.db[USER_DB_COLLECTION]
        self.create_user_object()

    def create_user_object(self):
        self.user = patch_config_for('user_authentication.user', 'User')

    def test_insert_user(self):
        self.user.insert_new_user(NAME, SURNAME, USERNAME, PASSWORD)

        # verify
        user = self.user_collection.find_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})
        self.verify_user(user)

    def test_user_is_not_inserted_when_exists(self):
        # insert user
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # try to insert user that already exists
        try:
            self.user.insert_new_user(NAME, SURNAME, USERNAME, PASSWORD)
        except UserExistsException as e:
            self.assertEqual(USERNAME, e.user)

        # verify second user was not inserted
        user = self.user_collection.find({'username': USERNAME, 'pwd_sha512': PWD_SHA512})
        self.assertEqual(1, len(list(user)))

    def test_get_user_from_db(self):
        # insert user
        self.user_collection.insert_one({'name': NAME, 'surname': SURNAME, 'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # get user
        user = self.user.get_user_from_db(USERNAME, PASSWORD)

        # verify
        self.verify_user(user)

    def test_get_user_from_db_return_none(self):
        self.assertIsNone(self.user.get_user_from_db(USERNAME, PASSWORD))

    def test_verify_user_returns_true_when_user_exists_in_db(self):
        # insert user
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})
        with patch('user_authentication.user.ldap_client.get_user_from_ldap_dir', return_value=None):
            self.assertTrue(self.user.verify_user(USERNAME, PASSWORD))
            self.assertEqual(USER_TYPES.LOCAL, self.user.user_type)

    def test_verify_user_returns_true_when_user_exists_in_ldap(self):
        with patch('user_authentication.user.ldap_client.config.get_ldap_base_dn', return_value='ou=users,dc=example,dc=com'):
            with patch('user_authentication.user.ldap_client.get_user_from_ldap_dir', return_value='ldap_user'):
                self.assertTrue(self.user.verify_user(USERNAME, PASSWORD))
                self.assertEqual(USER_TYPES.LDAP, self.user.user_type)

    def test_verify_user_returns_false_when_user_does_not_exits_neither_in_db_nor_in_ldap(self):
        with patch('user_authentication.user.ldap_client.get_user_from_ldap_dir', return_value=None):
            self.assertFalse(self.user.verify_user(USERNAME, PASSWORD))

    def test_get_users_return_two_users(self):
        # insert 2 users
        self.user_collection.insert_many(documents=[{'username': 'user1', 'pwd_sha512': PWD_SHA512},
                                                    {'username': 'user2', 'pwd_sha512': PWD_SHA512}])
        # get users
        users = self.user.get_users()

        self.assertEqual(2, len(users))
        self.assertEqual('user1', users[0].get('username'))
        self.assertEqual('user2', users[1].get('username'))

    def test_get_users_return_empty_list(self):
        self.assertEqual(0, len(self.user.get_users()))

    def test_delete_user(self):
        # insert user to be deleted
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # delete user
        self.user.delete_user(USERNAME)

        self.assertIsNone(self.user_collection.find_one({'username': USERNAME}))

    def test_change_user_password_returns_true_when_pwd_was_changed(self):
        # insert user
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # change pwd
        new_pwd = '1234'
        was_changed = self.user.change_password(USERNAME, PASSWORD, new_pwd)

        # verify
        self.assertTrue(was_changed)
        self.assertIsNotNone(self.user_collection.find_one({'username': USERNAME, 'pwd_sha512': get_hash_value(new_pwd)}))

    def test_change_user_password_returns_false_when_old_pwd_is_wrong(self):
        # insert user
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # change pwd
        new_pwd = '1234'
        was_changed = self.user.change_password(USERNAME, 'wrong_pwd', new_pwd)

        # verify
        self.assertFalse(was_changed)
        self.assertIsNone(self.user_collection.find_one({'username': USERNAME, 'pwd_sha512': get_hash_value(new_pwd)}))

    def test_change_user_password_returns_false_when_new_pwd_is_empty(self):
        # insert user
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # change pwd
        new_pwd = ''
        was_changed = self.user.change_password(USERNAME, 'wrong_pwd', new_pwd)

        # verify
        self.assertFalse(was_changed)
        self.assertIsNone(self.user_collection.find_one({'username': USERNAME, 'pwd_sha512': get_hash_value(new_pwd)}))

    def test_change_user_password_returns_false_when_new_pwd_is_none(self):
        # insert user
        self.user_collection.insert_one({'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # change pwd
        new_pwd = None
        was_changed = self.user.change_password(USERNAME, 'wrong_pwd', new_pwd)

        # verify
        self.assertFalse(was_changed)

    def test_modify_user(self):
        # insert user to be modified
        self.user_collection.insert_one({'name': NAME, 'surname': SURNAME, 'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # modify user
        new_name = 'modified name'
        new_surname = 'modified surname'
        new_username = 'modified username'
        self.user.modify_user(USERNAME, new_username, new_name, new_surname)

    def test_user_is_not_modified_when_new_username_exists(self):
        # insert two users
        self.user_collection.insert_many(documents=[{'name': NAME, 'surname': SURNAME, 'username': USERNAME, 'pwd_sha512': PWD_SHA512},
                                                    {'name': NAME, 'surname': SURNAME, 'username': 'username2', 'pwd_sha512': PWD_SHA512}])

        # modify user
        new_name = 'modified name'
        new_surname = 'modified surname'
        new_username = USERNAME
        self.user.modify_user('username2', new_username, new_name, new_surname)

        # verify
        user = self.user_collection.find_one({'username': 'username2'})
        self.assertIsNotNone(user)
        self.assertEqual(NAME, user.get('name'))
        self.assertEqual(SURNAME, user.get('surname'))
        self.assertEqual('username2', user.get('username'))

    def test_modify_user_when_new_username_equal_to_old_username(self):
        # insert two users
        self.user_collection.insert_one({'name': NAME, 'surname': SURNAME, 'username': USERNAME, 'pwd_sha512': PWD_SHA512})

        # modify user
        new_name = 'modified name'
        new_surname = 'modified surname'
        self.user.modify_user(USERNAME, USERNAME, new_name, new_surname)

        # verify
        user = self.user_collection.find_one({'username': USERNAME})
        self.assertIsNotNone(user)
        self.assertEqual(new_name, user.get('name'))
        self.assertEqual(new_surname, user.get('surname'))
        self.assertEqual(USERNAME, user.get('username'))

    def test_is_user_collection_empty_returns_false(self):
        self.user_collection.insert_one({'username': 'test'})
        self.assertFalse(self.user.is_user_collection_empty())

    def test_is_user_collection_empty_returns_true(self):
        self.assertTrue(self.user.is_user_collection_empty())

    def verify_user(self, user):
        self.assertIsNotNone(user)
        self.assertEqual(NAME, user.get('name'))
        self.assertEqual(SURNAME, user.get('surname'))
        self.assertEqual(USERNAME, user.get('username'))
        self.assertEqual(PWD_SHA512, user.get('pwd_sha512'))

    def tearDown(self):
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()

if __name__ == '__main__':
    unittest.main()
