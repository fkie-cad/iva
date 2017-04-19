import datetime


def generate_log_entry_for_new_alert(cve):
    return generate_log_entry('Alert generated due to ' + cve)


def generate_log_entry_for_added_cve(cve):
    return generate_log_entry(cve + ' was added')


def generate_log_entry_for_removed_cve(cve):
    return generate_log_entry(cve + ' was removed')


def generate_log_entry_for_changed_alert_status(old_status, new_status):
    return generate_log_entry('Alert status changed: ' + old_status + ' to ' + new_status)


def generate_log_entry(event):
    return {'date': get_date(), 'event': event}


def get_date():
    return datetime.datetime.utcnow()


