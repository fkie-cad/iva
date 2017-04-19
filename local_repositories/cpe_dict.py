from database import Database
from local_repositories.cve_search import CVESearchDB
from local_repositories import iva_formatter

IVA_CPE_COLLECTION = 'cpes'


class CPEDict:

    def __init__(self):
        self.iva_db = Database()
        self.cve_search_db = CVESearchDB()

    def update_cpe_dict(self):
        cpe_dict = []
        for cpe in self.cve_search_db.get_cpe_dict():
            formatted_cpe = iva_formatter.format_cpe(cpe)
            cpe_dict.append(formatted_cpe)
        self.update(cpe_dict)
        self.iva_db.close()

    def update(self, new_cpe_dict):
        self.iva_db.update_documents_in_collection(new_cpe_dict, iva_formatter.IVA_CPE_KEYS.uri, IVA_CPE_COLLECTION)

    def number_of_entries(self):
        return self.iva_db.get_number_of_documents_in_collection(IVA_CPE_COLLECTION)
