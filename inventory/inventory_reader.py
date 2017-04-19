import ast
from inventory import glpi_inventory


def read_inventory(file_path=None):
    if file_path is not None:
        return read_inventory_from_file(file_path)
    return glpi_inventory.read_inventory()


def read_inventory_from_file(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        return convert_list_elements_to_dict(f.readlines())


def convert_list_elements_to_dict(str_list):
    dict_list = []
    for s in str_list:
        dict_list.append(ast.literal_eval(s))
    return dict_list
