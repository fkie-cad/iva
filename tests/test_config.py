from urllib.parse import urljoin
import unittest
import configparser
import os
import config


CONFIG_FILE = 'config.ini'
TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, os.pardir))
PRODUCTION_CONFIG_FILE = os.path.join(ROOT_DIR, CONFIG_FILE)
TEST_CONFIG_FILE = os.path.join(ROOT_DIR, 'tests/resources/' + CONFIG_FILE)
DUMMY_CONFIG_FILE = os.path.join(ROOT_DIR, 'dummy/' + CONFIG_FILE)


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.expected_config = self.load_configuration(TEST_CONFIG_FILE)
        config.load_configuration_from_file(TEST_CONFIG_FILE)

    def test_config_files_exist(self):
        self.assertTrue(os.path.exists(PRODUCTION_CONFIG_FILE))
        self.assertTrue(os.path.exists(TEST_CONFIG_FILE))
        self.assertTrue(os.path.exists(DUMMY_CONFIG_FILE))

    def test_configuration_options_exist(self):
        production_config = self.load_configuration(PRODUCTION_CONFIG_FILE)
        dummy_config = self.load_configuration(DUMMY_CONFIG_FILE)
        test_config = self.load_configuration(TEST_CONFIG_FILE)

        self.verify_config_options_exist(production_config, PRODUCTION_CONFIG_FILE)
        self.verify_config_options_exist(dummy_config, DUMMY_CONFIG_FILE)
        self.verify_config_options_exist(test_config, TEST_CONFIG_FILE)

    def verify_config_options_exist(self, config_, config_file):
        self.assertIsNotNone(config_.get('database', 'host'), config_file)
        self.assertIsNotNone(config_.get('database', 'port'), config_file)
        self.assertIsNotNone(config_.get('database', 'name'), config_file)
        self.assertIsNotNone(config_.get('database', 'user'), config_file)
        self.assertIsNotNone(config_.get('database', 'password'), config_file)
        self.assertIsNotNone(config_.get('database', 'authentication'), config_file)
        self.assertIsNotNone(config_.get('inventory-database', 'host'), config_file)
        self.assertIsNotNone(config_.get('inventory-database', 'user'), config_file)
        self.assertIsNotNone(config_.get('inventory-database', 'password'), config_file)
        self.assertIsNotNone(config_.get('inventory-database', 'name'), config_file)
        self.assertIsNotNone(config_.get('frontend', 'host'), config_file)
        self.assertIsNotNone(config_.get('frontend', 'port'), config_file)
        self.assertIsNotNone(config_.get('cve-search', 'dir'), config_file)
        self.assertIsNotNone(config_.get('cve-search', 'db'), config_file)
        self.assertIsNotNone(config_.get('cve-search', 'url'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'host'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'port'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'user'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'password'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'sender'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'receiver'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'starttls'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'smtps'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'verify_server_cert'), config_file)
        self.assertIsNotNone(config_.get('smtp', 'ca_cert_file'), config_file)
        self.assertIsNotNone(config_.get('gpg', 'required'), config_file)
        self.assertIsNotNone(config_.get('gpg', 'home_dir'), config_file)
        self.assertIsNotNone(config_.get('gpg', 'pub_key_file'), config_file)
        self.assertIsNotNone(config_.get('ldap', 'host'), config_file)
        self.assertIsNotNone(config_.get('ldap', 'port'), config_file)
        self.assertIsNotNone(config_.get('ldap', 'base_dn'), config_file)
        self.assertIsNotNone(config_.get('ldap', 'tls'), config_file)
        self.assertIsNotNone(config_.get('ldap', 'cacert'), config_file)
        self.assertIsNotNone(config_.get('logging', 'file'), config_file)

    def test_get_db_host(self):
        expected_host = self.expected_config.get('database', 'host')
        host = config.get_database_host()
        self.assertEqual(expected_host, host)

    def test_get_db_port(self):
        expected_port = self.expected_config.getint('database', 'port')
        port = config.get_database_port()
        self.assertEqual(expected_port, port)

    def test_get_database_name(self):
        expected_db_name = self.expected_config.get('database', 'name')
        db_name = config.get_database_name()
        self.assertEqual(expected_db_name, db_name)

    def test_get_database_user(self):
        expected_db_user = self.expected_config.get('database', 'user')
        db_user = config.get_database_user()
        self.assertEqual(expected_db_user, db_user)

    def test_get_database_password(self):
        expected_db_password = self.expected_config.get('database', 'password')
        db_password = config.get_database_password()
        self.assertEqual(expected_db_password, db_password)

    def test_is_database_authentication_enabled(self):
        self.assertEqual(self.get_boolean_value_for('database', 'authentication'),
                         config.is_database_authentication_enabled())

    def test_get_cve_search_db_name(self):
        expected_db_name = self.expected_config.get('cve-search', 'db')
        db_name = config.get_cve_search_db_name()
        self.assertEqual(expected_db_name, db_name)

    def test_get_cve_search_dir(self):
        expected_dir = self.expected_config.get('cve-search', 'dir')
        dir_ = config.get_cve_search_dir()
        self.assertEqual(expected_dir, dir_)

    def test_get_cve_search_url(self):
        expected_url = self.add_cve_path_to_url()
        url = config.get_cve_search_url()
        self.assertEqual(expected_url, url)

    def add_cve_path_to_url(self):
        return urljoin(self.expected_config.get('cve-search', 'url'), '/cve/')

    def test_get_frontend_host(self):
        expected_host = self.expected_config.get('frontend', 'host')
        host = config.get_frontend_host()
        self.assertEqual(expected_host, host)

    def test_get_frontend_port(self):
        expected_port = self.expected_config.get('frontend', 'port')
        port = config.get_frontend_port()
        self.assertEqual(expected_port, port)

    def test_get_log_file(self):
        expected_log_file = self.expected_config.get('logging', 'file')
        log_file = config.get_log_file()
        self.assertEqual(expected_log_file, log_file)

    def test_get_inventory_database_host(self):
        expected_host = self.expected_config.get('inventory-database', 'host')
        host = config.get_inventory_database_host()
        self.assertEqual(expected_host, host)

    def test_get_inventory_database_user(self):
        expected_user = self.expected_config.get('inventory-database', 'user')
        user = config.get_inventory_database_user()
        self.assertEqual(expected_user, user)

    def test_get_glpi_db_mysql_password(self):
        expected_password = self.expected_config.get('inventory-database', 'password')
        password = config.get_inventory_database_password()
        self.assertEqual(expected_password, password)

    def test_get_glpi_db_name(self):
        expected_db_name = self.expected_config.get('inventory-database', 'name')
        db_name = config.get_glpi_db_name()
        self.assertEqual(expected_db_name, db_name)

    def test_get_smpt_server_host(self):
        expected_host = self.expected_config.get('smtp', 'host')
        host = config.get_smtp_server_host()
        self.assertEqual(expected_host, host)

    def test_get_smpt_server_port(self):
        expected_port = self.expected_config.get('smtp', 'port')
        port = config.get_smtp_server_port()
        self.assertEqual(expected_port, port)

    def test_get_smtp_user(self):
        expected_user = self.expected_config.get('smtp', 'user')
        user = config.get_smtp_user()
        self.assertEqual(expected_user, user)

    def test_get_smtp_password(self):
        expected_password = self.expected_config.get('smtp', 'password')
        password = config.get_smtp_password()
        self.assertEqual(expected_password, password)

    def test_get_smtp_sender(self):
        expected_sender = self.expected_config.get('smtp', 'sender')
        sender = config.get_smtp_sender()
        self.assertEqual(expected_sender, sender)

    def test_get_smtp_receiver(self):
        expected_receiver = self.expected_config.get('smtp', 'receiver')
        receiver = config.get_smtp_receiver()
        self.assertEqual(expected_receiver, receiver)

    def test_is_smtp_starttls_enabled(self):
        self.assertEqual(self.get_boolean_value_for('smtp', 'starttls'), config.is_smtp_starttls_enabled())

    def test_is_smtps_enabled(self):
        self.assertEqual(self.get_boolean_value_for('smtp', 'smtps'), config.is_smtps_enabled())

    def test_verify_smtp_server_cert(self):
        self.assertEqual(self.get_boolean_value_for('smtp', 'verify_server_cert'), config.is_verify_smtp_server_cert_enabled())

    def test_get_smtp_ca_cert_file(self):
        self.assertEqual(self.expected_config.get('smtp', 'ca_cert_file'), config.get_smtp_ca_cert_file())

    def test_is_gpg_encryption_enabled(self):
        self.assertEqual(self.get_boolean_value_for('gpg', 'required'), config.is_gpg_encryption_enabled())

    def get_gpg_home_dir(self):
        self.assertEqual(self.expected_config.get('gpg', 'home_dir'), config.get_gpg_home_dir())

    def get_gpg_pub_key_file(self):
        self.assertEqual(self.expected_config.get('gpg', 'pub_key_file'), config.get_gpg_pub_key_file())

    def test_get_ldap_host(self):
        expected_host = self.expected_config.get('ldap', 'host')
        host = config.get_ldap_host()
        self.assertEqual(expected_host, host)

    def test_get_ldap_port(self):
        expected_port = self.expected_config.getint('ldap', 'port')
        port = config.get_ldap_port()
        self.assertEqual(expected_port, port)

    def test_get_ldap_base_dn(self):
        expected_base_dn = self.expected_config.get('ldap', 'base_dn')
        base_dn = config.get_ldap_base_dn()
        self.assertEqual(expected_base_dn, base_dn)

    def test_is_ldap_tls_enabled(self):
        self.assertEqual(self.get_boolean_value_for('ldap', 'tls'), config.is_ldap_tls_enabled())

    def test_get_ldap_cacert_file_path(self):
        expected_ca_cert = self.expected_config.get('ldap', 'cacert')
        ca_cert = config.get_ldap_cacert_file_path()
        self.assertEqual(expected_ca_cert, ca_cert)

    def get_boolean_value_for(self, block, option):
        try:
            return self.expected_config.getboolean(block, option)
        except ValueError:
            return False

    def load_configuration(self, config_file):
        config_ = configparser.RawConfigParser()
        config_.read(config_file)
        return config_


if __name__ == '__main__':
    unittest.main()
