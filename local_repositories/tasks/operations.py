import traceback
import logger
from inventory.inventory import Inventory
from inventory.software_cve_matches import CVEMatches
from local_repositories import cve_search
from local_repositories.cpe_dict import CPEDict
from local_repositories.cve_feeds import CVEFeeds
from matching.cve_matcher import CVEMatcher


def update_db():
    logger.info('DB UPDATE - starting daily update')
    update_cve_search_db()
    update_iva_db()
    search_cves()
    logger.info('DB UPDATE - daily update finished')


def update_cve_search_db():
    logger.info('DB UPDATE - updating cve-search DB')
    try:
        cve_search.update_db()
        logger.info('DB UPDATE - cve-search DB update finished')
    except Exception:
        logger.info('DB UPDATE - failed to update cve-search DB')
        log_traceback()


def update_iva_db():
    logger.info('DB UPDATE - update IVA DB')
    update_cpe_dict()
    update_cve_feeds()
    logger.info('DB UPDATE - update IVA DB finished')


def update_cpe_dict():
    logger.info('DB UPDATE - updating CPE dictionary')
    try:
        CPEDict().update_cpe_dict()
        logger.info('DB UPDATE - updating CPE dictionary finished')
    except Exception:
        logger.info('DB UPDATE - failed to update CPE dictionary')
        log_traceback()


def update_cve_feeds():
    logger.info('DB UPDATE - updating CVE feeds')
    try:
        CVEFeeds().update_cve_feeds()
        logger.info('DB UPDATE - updating CVE feeds finished')
    except Exception:
        logger.info('DB UPDATE - failed to update CVE feeds')
        log_traceback()


def search_cves():
    logger.info('DB UPDATE - search CVE matches for software products')
    search_cves_and_update_db()
    logger.info('DB UPDATE - search CVE matches finished')


def populate_db():
    logger.info('DB UPDATE - populating cve-search DB')
    try:
        cve_search.populate_db()
        logger.info('DB UPDATE - populating cve-search finished')
    except Exception:
        logger.error('DB UPDATE - failed to populate cve-search DB')
        log_traceback()


def repopulate_db():
    logger.info('DB UPDATE - repopulating cve-search DB')
    try:
        cve_search.repopulate_db()
        logger.info('DB UPDATE - repopulating cve-search finished')
    except Exception:
        logger.error('DB UPDATE - failed to repopulate cve-search DB')
        log_traceback()


def search_cves_and_update_db():
    for software in get_software_products():
        update_software_cve_matches(software)


def get_software_products():
    return Inventory().get_software_products_with_assigned_cpe()


def update_software_cve_matches(software):
    CVEMatches().insert_software_cve_matches(software.get('id'), get_cve_matches(software))


def get_cve_matches(software):
    return CVEMatcher().search_cves_for_cpe(get_uri_binding(software))


def get_uri_binding(software):
    return software.get('cpe').get('uri_binding')


def log_traceback():
    logger.error('DB UPDATE - ' + str(traceback.format_exc()))