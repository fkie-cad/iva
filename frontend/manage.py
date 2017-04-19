#!/usr/bin/env python
import os
import sys
from django.core.management import execute_from_command_line

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)

import config


def set_django_settings_env_var():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend_env.settings")


def set_iva_config_file_env_var():
    if len(sys.argv) == 4:
        os.environ.setdefault("IVA_CONFIG_FILE", sys.argv.pop())


def load_iva_config():
    config.load_configuration_from_file(os.environ.get("IVA_CONFIG_FILE"))


if __name__ == "__main__":
    set_django_settings_env_var()
    set_iva_config_file_env_var()
    load_iva_config()
    execute_from_command_line(sys.argv)
