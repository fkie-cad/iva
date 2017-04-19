from database import Database
from local_repositories.cve_search import CVESearchDB
from local_repositories import iva_formatter

IVA_CVE_COLLECTION = 'cves'
BATCH_SIZE = 4000


class CVEFeeds:

    def __init__(self):
        self.iva_db = Database()
        self.cve_search_db = CVESearchDB()

    def update_cve_feeds(self):
        self.drop_cve_feeds()
        skip = 0
        number_cves_to_update = self.cve_search_db.get_number_of_cves_entries()
        while number_cves_to_update > BATCH_SIZE:
            self.update_cve_feeds_in_range(skip, BATCH_SIZE)
            skip += BATCH_SIZE
            number_cves_to_update -= BATCH_SIZE
        if number_cves_to_update > 0:
            self.update_cve_feeds_in_range(skip, 0)
        self.close()

    def update_cve_feeds_in_range(self, skip, limit):
        cve_feeds = []
        cves = self.cve_search_db.get_cve_feeds(skip, limit)
        number_cves = len(cves)
        for i in range(number_cves):
            cve_feeds.append(iva_formatter.format_cve(cves.pop()))
        del cves
        self.update(cve_feeds)

    def update(self, new_cve_entries):
        self.iva_db.insert_documents_in_collection(new_cve_entries, IVA_CVE_COLLECTION)

    def drop_cve_feeds(self):
        self.iva_db.drop_collection(IVA_CVE_COLLECTION)

    def number_of_entries(self):
        return self.iva_db.get_number_of_documents_in_collection(IVA_CVE_COLLECTION)

    def close(self):
        self.iva_db.close()
        self.cve_search_db.close()
