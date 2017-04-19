import logger
import datetime
from database import Database
from wfn.encoding import Decoder
from collections import namedtuple
from alerts.alert_sender import EmailSender
from inventory.inventory import INVENTORY_DB_COLLECTION
from alerts.alerts_logger import generate_log_entry_for_added_cve, generate_log_entry_for_new_alert
from alerts.alerts_logger import generate_log_entry_for_removed_cve, generate_log_entry_for_changed_alert_status

ALERTS_DB_COLLECTION = 'alerts'
STATUS = namedtuple('STATUS', ['new', 'sent', 'closed', 'removed'])('new', 'sent', 'closed', 'removed')


class Alerts:

    def __init__(self):
        self.db = Database()

    def insert_alert(self, software_id, cve_id):
        if not self.alert_for_software_exists(software_id):
            self.insert_new_alert_for_inventory_item(software_id, cve_id)
        else:
            self.add_new_cve_to_alert(software_id, cve_id)

    def alert_for_software_exists(self, software_id):
        return self.db.exist_doc_in_collection(get_id_as_dict(software_id), ALERTS_DB_COLLECTION)

    def insert_new_alert_for_inventory_item(self, item_id, cve_id):
        self.db.insert_document_in_collection(create_new_alert_dict(item_id, cve_id), ALERTS_DB_COLLECTION)

    def add_new_cve_to_alert(self, item_id, new_cve):
        alert = self.get_software_alert(item_id)
        self.update_alert(item_id, generate_update_for_add_new_cve(alert, new_cve))
        self.change_status_to_new(alert, item_id)

    def change_status_to_new(self, alert, item_id):
        if not is_status_new(alert):
            self.change_alert_status(item_id, STATUS.new)

    def remove_cve_from_alert(self, item_id, cve):
        alert = self.get_software_alert(item_id)
        self.update_alert(item_id, generate_update_for_remove_cve(alert, cve))
        self.change_status_to_removed(alert, item_id)

    def change_status_to_removed(self, alert, item_id):
        if len(alert.get('cves')) == 0:
            self.change_alert_status(item_id, STATUS.removed)

    def change_alert_status(self, software_id, new_status):
        alert = self.get_software_alert(software_id)
        if can_status_be_changed(alert, new_status):
            self.removed_cves_from_alert(software_id, alert, new_status)
            self.update_alert(software_id, generate_update_for_change_status_alert(alert, new_status))
        return False

    def removed_cves_from_alert(self, software_id, alert, new_status):
        if new_status == STATUS.removed:
            for cve in alert.get('cves'):
                self.remove_cve_from_alert(software_id, cve)

    def update_alert(self, item_id, update):
        self.db.update_document_in_collection(get_id_as_dict(item_id), update, ALERTS_DB_COLLECTION)

    def get_software_alert(self, software_id):
        return self.db.search_document_in_collection(get_id_as_dict(software_id), ALERTS_DB_COLLECTION)

    def get_alerts(self):
        alerts = []
        alerts_status_new = self.get_alerts_of_status_sorted_by_date(STATUS.new)
        alerts_status_sent = self.get_alerts_of_status_sorted_by_date(STATUS.sent)
        alerts_status_closed = self.get_alerts_of_status_sorted_by_date(STATUS.closed)
        alerts_status_removed = self.get_alerts_of_status_sorted_by_date(STATUS.removed)
        alerts.extend(alerts_status_new)
        alerts.extend(alerts_status_sent)
        alerts.extend(alerts_status_closed)
        alerts.extend(alerts_status_removed)
        return alerts

    def get_alerts_of_status_sorted_by_date(self, status):
        return list(sort_alerts_by_date(self.db.search_documents_in_collection({'status': status}, ALERTS_DB_COLLECTION)))

    def update_notes(self, software_id, notes):
        self.db.update_document_in_collection(get_id_as_dict(software_id), {'notes': notes}, ALERTS_DB_COLLECTION)

    def get_number_of_new_alerts(self):
        return self.get_number_of_alerts_by_status(STATUS.new)

    def get_number_of_sent_alerts(self):
        return self.get_number_of_alerts_by_status(STATUS.sent)

    def get_number_of_alerts_by_status(self, status):
        return self.db.get_number_of_documents_in_collection(ALERTS_DB_COLLECTION, {'status': status})

    def send_sw_alert_by_email(self, software_id):
        software = self.get_software(software_id)
        alert = self.get_software_alert(software_id)
        sw_alert_email = create_sw_alert_email(alert, software)
        return self.send(sw_alert_email, software)

    def send(self, alert_mail, software):
        sw_string = software.get('product') + ' ' + software.get('product') + ' ' + software.get('version')
        logger.info('ALERTS - sending notification for ' + sw_string)
        was_sent = EmailSender().send(alert_mail)
        if was_sent:
            logger.info('ALERTS - notification for ' + sw_string + ' successfully sent')
            self.change_alert_status(software.get('id'), new_status=STATUS.sent)
            return True
        logger.error('ALERTS - failed to sent notification for ' + sw_string)
        return False

    def get_software(self, software_id):
        return self.db.search_document_in_collection({'id': software_id}, INVENTORY_DB_COLLECTION)


def create_new_alert_dict(software_id, cve_id):
    return {'generated_on': datetime.datetime.utcnow(),
            'software_id': software_id,
            'cves': [cve_id],
            'status': STATUS.new,
            'log': [generate_log_entry_for_new_alert(cve_id)],
            'notes': ''}


def get_id_as_dict(item_id):
    return {'software_id': item_id}


def update_log(alert, log_entry):
    log = alert.get('log')
    log.append(log_entry)
    return log


def update_cves(alert, cve, option):
    cves = alert.get('cves')
    if option == 'append':
        cves.append(cve)
    elif option == 'remove':
        cves.remove(cve)
    return cves


def sort_alerts_by_date(alerts):
    return alerts.sort('generated_on', 1)


def can_status_be_changed(alert, new_status):
    if alert is not None:
        if (new_status == 'new' and len(alert.get('cves')) == 0) and current_status_close_or_removed(alert.get('status')):
            return False
        return True
    return False


def current_status_close_or_removed(status):
    return status == STATUS.closed or status == STATUS.removed


def generate_update_for_add_new_cve(alert, new_cve):
    return {'cves': update_cves(alert, new_cve, 'append'),
            'log': update_log(alert, generate_log_entry_for_added_cve(new_cve))}


def generate_update_for_remove_cve(alert, cve):
    return {'cves': update_cves(alert, cve, 'remove'),
            'log': update_log(alert, generate_log_entry_for_removed_cve(cve))}


def generate_update_for_change_status_alert(alert, new_status):
    return {'status': new_status,
            'log': update_log(alert, generate_log_entry_for_changed_alert_status(alert.get('status'), new_status))}


def is_status_new(alert):
    return alert.get('status') == STATUS.new


def create_sw_alert_email(alert, software):
    email = 'Generated on: ' + str(alert.get('generated_on')) + '\n\n' \
            'Software ID: ' + software.get('id') + '\n\n' \
            'Product: ' + software.get('product') + '\n\n' \
            'Vendor: ' + software.get('vendor') + '\n\n' \
            'Version: ' + software.get('version') + '\n\n' \
            'CPE: ' + get_software_cpe(software) + '\n\n' \
            'CVEs: ' + str(alert.get('cves')) + '\n\n' \
            'Status: ' + alert.get('status') + '\n\n' \
            'Log:\n' + format_log(alert.get('log')) + '\n' \
            'Notes: ' + alert.get('notes')
    return email


def get_software_cpe(software):
    return Decoder.decode_non_alphanumeric_characters((software.get('cpe').get('uri_binding')))


def format_log(log):
    log_str = ''
    for entry in log:
        log_str += str(entry.get('date')) + ': '+entry.get('event')+'\n'
    return log_str
