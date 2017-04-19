# Inventory Vulnerability Analysis (IVA)
#
# Copyright 2017 Fraunhofer FKIE
#
# IVA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IVA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IVA in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import config
import server_runner
from collections import namedtuple
from user_authentication.user import User

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILES = namedtuple('CONFIG_FILES', ['default', 'test'])('/config.ini', '/dummy/config.ini')
TEST_MODE_OPT = 'test'


def main():
    config_file = get_config_file()
    config.load_configuration_from_file(config_file)
    server_runner.run_iva_server(config_file)
    server_runner.run_cve_search_server()
    create_dummy_user_if_no_user_exists()
    return 0


def get_config_file():
    if is_test_mode():
        return ROOT_DIR + CONFIG_FILES.test
    return ROOT_DIR + CONFIG_FILES.default


def create_dummy_user_if_no_user_exists():
    user = User()
    if user.is_user_collection_empty() or is_test_mode():
        user.create_dummy_user()


def is_test_mode():
    if len(sys.argv) > 1:
        return sys.argv[1] == TEST_MODE_OPT
    return False


if __name__ == '__main__':
    sys.exit(main())
