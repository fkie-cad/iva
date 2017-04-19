import pycountry
from django import template
from alerts.alerts import Alerts
from inventory.inventory import Inventory
from local_repositories.tasks.scheduler import TaskScheduler

register = template.Library()


@register.simple_tag
def number_new_alerts():
    alerts = Alerts()
    new_alerts = alerts.get_number_of_new_alerts()
    sent_alerts = alerts.get_number_of_sent_alerts()
    return new_alerts + sent_alerts


@register.simple_tag
def number_new_glpi_items():
    return len(Inventory().get_software_products_without_assigned_cpe())


@register.simple_tag
def scheduled_tasks():
    return TaskScheduler().get_number_of_scheduled_tasks()


@register.simple_tag
def get_country_name(code):
    try:
        return pycountry.languages.get(iso639_1_code=code).name
    except:
        return code



