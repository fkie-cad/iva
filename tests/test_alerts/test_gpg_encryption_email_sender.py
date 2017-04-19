import os
import gnupg
import config
import unittest
from unittest.mock import patch
from alerts.alert_sender import EmailSender

TEST_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.abspath(os.path.join(TEST_FILE_PATH, os.pardir))
GPG_DIR = os.path.join(TEST_DIR, 'resources/gpg/')
PUB_KEY_FILE = os.path.join(GPG_DIR, 'iva_pub.asc')
PRI_KEY_FILE = os.path.join(GPG_DIR, 'iva_pri.asc')
BODY = 'email body that must be encrypted when is required'

config.reload_configuration(os.path.join(TEST_DIR, 'resources/config.ini'))


class TestGPG(unittest.TestCase):

    def setUp(self):
        self.gpg = gnupg.GPG(homedir=GPG_DIR)

    def test_email_body_is_encrypted_with_gpg(self):
        with patch('config.is_gpg_encryption_enabled', return_value=True):
            with patch('config.get_gpg_home_dir', return_value=GPG_DIR):
                with patch('config.get_gpg_pub_key_file', return_value=PUB_KEY_FILE):
                    self.verify_encrypted_body(self.create_email())

    def test_email_body_is_not_encrypted(self):
        with patch('config.is_gpg_encryption_enabled', return_value=False):
            email = self.create_email()
            self.assertEqual(BODY, email.get_payload())

    def create_email(self):
        return EmailSender().create_email('subject', BODY)

    def verify_encrypted_body(self, email):
        self.import_keys()
        self.assertEqual(self.get_decrypted_body(email), BODY)

    def import_keys(self):
        with open(PRI_KEY_FILE, 'r') as f:
            self.gpg.import_keys(f.read())

    def get_decrypted_body(self, email):
        return str(self.gpg.decrypt(email.get_payload()))


if __name__ == '__main__':
    unittest.main()
