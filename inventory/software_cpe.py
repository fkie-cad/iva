from alerts.alerts import Alerts
from database import Database
from inventory.inventory import INVENTORY_DB_COLLECTION
from wfn.wfn_converter import WFNConverter


class SoftwareCPE:

    def __init__(self):
        self.db = Database()
        self.alerts = Alerts()

    def create_sw_cpe_dict(self, wfn):
        return {'wfn': wfn, 'uri_binding': bind_wfn_to_uri(wfn)}

    def assign_cpe_to_software(self, cpe, software_id):
        self.db.update_document_in_collection({'id': software_id}, {'cpe': cpe}, INVENTORY_DB_COLLECTION)

    def update_software_cpe(self, software_id, new_wfn):
        self.update(software_id, bind_wfn_to_uri(new_wfn), new_wfn)
        self.alerts.change_alert_status(software_id, 'removed')

    def update(self, software_id, new_uri, new_wfn):
        self.db.update_document_in_collection({'id': software_id},
                                              {'cpe': {'uri_binding': new_uri, 'wfn': new_wfn}, 'cve_matches': []},
                                              INVENTORY_DB_COLLECTION)

    def get_software_cpe_by_id(self, software_id):
        software = self.get_software({'id': software_id})
        return get_cpe_from_software_dict(software)

    def get_software_cpe_by_uri(self, uri_binding):
        software = self.get_software({'cpe.uri_binding': uri_binding})
        return get_cpe_from_software_dict(software)

    def get_software(self, search_condition):
        return self.db.search_document_in_collection(search_condition, INVENTORY_DB_COLLECTION)


def bind_wfn_to_uri(wfn):
    return WFNConverter().convert_wfn_to_uri(wfn)


def get_cpe_from_software_dict(software):
    if software is not None:
        return software.get('cpe')