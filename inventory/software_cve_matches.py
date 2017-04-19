from database import Database
from alerts.alerts import Alerts
from inventory.inventory import INVENTORY_DB_COLLECTION, Inventory
from wfn.wfn_converter import WFNConverter
from wfn.wfn_comparator import versions_equal


class CVEMatches:

    def __init__(self):
        self.inventory = Inventory()
        self.alerts = Alerts()
        self.db = Database()

    def insert_software_cve_matches(self, software_id, matches):
        new_matches = []
        matches = format_matches(matches)
        for old_match in self.get_software_cve_matches(software_id):
            is_match = False
            for match in matches:
                if old_match.get('cve_id') == match.get('cve_id'):
                    new_matches.append(old_match)
                    matches.remove(match)
                    is_match = True
                    break
            if not is_match:
                self.remove_old_cve_match_from_alert(old_match, software_id)
        new_matches.extend(matches)
        sw = self.inventory.get_software_by_id(software_id)
        self.update_matches_in_db(software_id, sort_cve_matches_by_version(new_matches, get_sw_version(sw)))

    def remove_old_cve_match_from_alert(self, old_match, software_id):
        if is_cve_match_positive(old_match):
            self.alerts.remove_cve_from_alert(software_id, old_match.get('cve_id'))

    def add_new_cve_match_to_software(self, software_id, new_match):
        cve_matches = self.get_software_cve_matches(software_id)
        self.update_matches_in_db(software_id, add_new_match_to_list(cve_matches, format_match(new_match)))

    def set_cve_matches_group_as_removed(self, software_id, cve_id_master):
        group = self.get_software_cve_matches_with_same_cpe_entries_as_cve(software_id, cve_id_master)
        for match in group:
            self.set_cve_match_as_removed(software_id, match.get('cve_id'))

    def set_cve_match_as_removed(self, software_id, cve_id):
        self.update_cve_match_status(software_id, cve_id, 'removed', 1)

    def restore_cve_matches_group(self, software_id, cve_id_master):
        group = self.get_software_cve_matches_with_same_cpe_entries_as_cve(software_id, cve_id_master)
        for match in group:
            self.restore_cve_match(software_id, match.get('cve_id'))

    def restore_cve_match(self, software_id, cve_id):
        self.update_cve_match_status(software_id, cve_id, 'removed', 0)

    def set_cve_matches_group_as_positive(self, software_id, cve_id_master):
        group = self.get_software_cve_matches_with_same_cpe_entries_as_cve(software_id, cve_id_master)
        for match in group:
            self.set_cve_match_as_positive(software_id, match.get('cve_id'))

    def set_cve_match_as_positive(self, software_id, cve_id):
        self.update_cve_match_status(software_id, cve_id, 'positive', 1)
        self.alerts.insert_alert(software_id, cve_id)

    def set_cve_matches_group_as_negative(self, software_id, cve_id_master):
        group = self.get_software_cve_matches_with_same_cpe_entries_as_cve(software_id, cve_id_master)
        for match in group:
            self.set_cve_match_as_negative(software_id, match.get('cve_id'))

    def set_cve_match_as_negative(self, software_id, cve_id):
        self.update_cve_match_status(software_id, cve_id, 'positive', 0)
        self.alerts.remove_cve_from_alert(software_id, cve_id)

    def update_cve_match_status(self, software_id, cve_id, field, status):
        matches = self.get_software_cve_matches(software_id)
        for match in matches:
            if match.get('cve_id') == cve_id:
                match.update({field: status})
                self.update_matches_in_db(software_id, matches)
                break

    def get_software_cve_matches_with_same_cpe_entries_as_cve(self, software_id, cve_id):
        cve_matches = self.get_software_cve_matches(software_id)
        cve_match_a = get_cve_match_from_matches(cve_id, cve_matches)
        matches_with_same_cpes = []
        for cve_match_b in cve_matches:
            if equal_removed_and_positive_status(cve_match_a, cve_match_b):
                if equal_cpe_entries(get_cpe_entries_from_cve(cve_match_a), get_cpe_entries_from_cve(cve_match_b)):
                    matches_with_same_cpes.append(cve_match_b)
        return matches_with_same_cpes

    def get_software_cve_matches(self, software_id):
        software = self.get_software(software_id)
        return get_sw_cve_matches(software)

    def get_vulnerable_software_items(self):
        vulnerable_software = []
        for software in self.get_software_items():
            if is_vulnerable(software):
                vulnerable_software.append(software)
        return vulnerable_software

    def exist_cve_matches_for_software(self, software_id):
        return len(self.get_software_cve_matches(software_id)) > 0

    def get_software_items(self):
        return self.db.get_documents_from_collection(INVENTORY_DB_COLLECTION)

    def remove_software_cve_matches(self, software_id):
        self.update_matches_in_db(software_id, [])

    def update_matches_in_db(self, software_id, matches):
        self.db.update_document_in_collection({'id': software_id}, {'cve_matches': matches}, INVENTORY_DB_COLLECTION)

    def get_software(self, software_id):
        return self.db.search_document_in_collection({'id': software_id}, INVENTORY_DB_COLLECTION)

    def get_cve_matches(self, filters=None):
        cve_matches = []
        for software in self.inventory.get_inventory():
            append_software_matches_to_list(software, cve_matches)
        return filter_matches(filters, cve_matches)

    def get_vendor_product_cve_matches(self, vendor='all', product='all', filters=None):
        if vendor != 'all':
            cve_matches = []
            for software in self.inventory.get_inventory():
                if is_vendor_and_product(vendor, product, software):
                    append_software_matches_to_list(software, cve_matches)
            return filter_matches(filters, cve_matches)
        return self.get_cve_matches(filters)


def sort_cve_matches_by_version(cve_matches, version):
        return sorted(cve_matches, key=lambda cve: has_cpe_with_equal_version(cve, version), reverse=True)


def has_cpe_with_equal_version(cve_match, version):
    cpe_entries = get_cpe_entries_from_cve(cve_match)
    for uri in cpe_entries:
        if versions_equal(get_version_from_uri(uri), version):
            return True
    return False


def format_matches(matches):
    formatted_matches = []
    for match in matches:
        formatted_matches.append(format_match(match))
    return formatted_matches


def format_match(match):
    del match['cve_summary']
    match['cpe_entries'] = get_uri_bindings_from_cpes(match.get('cpe_entries'))
    match['positive'] = 0
    match['removed'] = 0
    return match


def get_uri_bindings_from_cpes(cpe_entries):
    uri_bindings = []
    for cpe in cpe_entries:
        uri_bindings.append(cpe.get('uri_binding'))
    return uri_bindings


def add_new_match_to_list(matches, new_match):
    matches.append(new_match)
    return matches


def is_vulnerable(software):
    for match in get_sw_cve_matches(software):
        if is_cve_match_positive(match):
            return True
    return False


def append_software_matches_to_list(software, list_):
    for match in get_sw_cve_matches(software):
        list_.append(create_sw_cve_match(match, software))
    del software['cve_matches']


def create_sw_cve_match(match, software):
    return {'cve_id': match.get('cve_id'), 'cpe_entries': match.get('cpe_entries'),
            'removed': match.get('removed'), 'positive': match.get('positive'), 'software': software}


def filter_matches(filters, matches):
    if filters is not None:
        if 'hide_removed' in filters:
            matches = discard_removed_matches(matches)
        if 'ordered_by_year_desc' in filters:
            matches = sorted(matches, key=lambda k: k['cve_id'], reverse=True)
        if 'ordered_by_year_asc' in filters:
            matches = sorted(matches, key=lambda k: k['cve_id'], reverse=False)
    return matches


def discard_removed_and_update_matches(software):
    software.update({'cve_matches': discard_removed_matches(get_sw_cve_matches(software))})


def discard_removed_matches(matches):
    not_removed_matches = []
    for match in matches:
        if not is_cve_match_removed(match):
            not_removed_matches.append(match)
    return not_removed_matches


def is_vendor_and_product(vendor, product, software):
    if software.get('cpe') is not None:
        if vendor == get_sw_vendor(software) and (product == 'all' or product == get_sw_product(software)):
            return True
    return False


def equal_cpe_entries(cpe_entries_a, cpe_entries_b):
    return set(cpe_entries_a) == set(cpe_entries_b)


def get_cve_match_from_matches(cve_id, cve_matches):
        for match in cve_matches:
            if match.get('cve_id') == cve_id:
                return match


def equal_removed_and_positive_status(cve_match_a, cve_match_b):
        return cve_match_a.get('removed') == cve_match_b.get('removed') and \
               cve_match_a.get('positive') == cve_match_b.get('positive')


def is_cve_match_positive(match):
    return match.get('positive') == 1


def is_cve_match_removed(match):
    return match.get('removed') == 1


def get_sw_product(software):
    return software.get('cpe').get('wfn').get('product')


def get_sw_vendor(software):
    return software.get('cpe').get('wfn').get('vendor')


def get_sw_version(software):
    return software.get('cpe').get('wfn').get('version')


def get_sw_cve_matches(software):
    return software.get('cve_matches')


def get_cpe_entries_from_cve(cve_match):
    return cve_match.get('cpe_entries')


def get_version_from_uri(uri):
    return WFNConverter().convert_cpe_uri_to_wfn(uri).get('version')