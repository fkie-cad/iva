import hashlib
from database import Database
from inventory import inventory_reader

INVENTORY_DB_COLLECTION = 'inventory'


class Inventory:

    def __init__(self):
        self.db = Database()

    def insert_new_software_products_to_db(self):
        for software in inventory_reader.read_inventory():
            self.insert_software_in_db(software)

    def insert_software_in_db(self, software):
        software = Software(software)
        if not self.exists_in_db(software):
            self.db.insert_document_in_collection(software.get(), INVENTORY_DB_COLLECTION)

    def exists_in_db(self, software):
        return self.db.exist_doc_in_collection({'id': software.get_id()}, INVENTORY_DB_COLLECTION)

    def search_software_products_without_assigned_cpe(self, search_term):
        sw_products_without_cpe = self.get_software_products_without_assigned_cpe()
        if search_term != '' and search_term is not None:
            sw_products = []
            for sw in sw_products_without_cpe:
                search_term = str(search_term).lower()
                sw_product = str(sw.get('product')).lower()
                sw_vendor = str(sw.get('vendor')).lower()
                if (search_term in sw_product) or (search_term in sw_vendor):
                    sw_products.append(sw)
            return sw_products
        return sw_products_without_cpe

    def get_software_products_without_assigned_cpe(self):
        products_without_cpe = []
        for software in self.get_inventory():
            if not has_cpe(software):
                products_without_cpe.append(software)
        return products_without_cpe

    def get_software_products_with_assigned_cpe(self):
        products_with_cpe = []
        for software in self.get_inventory():
            if has_cpe(software):
                products_with_cpe.append(software)
        return products_with_cpe

    def get_inventory(self):
        return sort_software_products_by_vendor(list(self.db.get_documents_from_collection(INVENTORY_DB_COLLECTION)))

    def get_software_by_id(self, software_id):
        return self.db.search_document_in_collection({'id': software_id}, INVENTORY_DB_COLLECTION)

    def get_vendors(self):
        return self.get_wfn_values_for_attribute('vendor')

    def get_products(self):
        return self.get_wfn_values_for_attribute('product')

    def get_vendor_products(self, vendor):
        products = []
        for software in self.get_inventory():
            cpe = software.get('cpe')
            if cpe is not None:
                wfn = cpe.get('wfn')
                v = wfn.get('vendor')
                p = wfn.get('product')
                if v == vendor and p not in products:
                    products.append(p)
        return products

    def get_wfn_values_for_attribute(self, attribute):
        values = []
        for software in self.get_inventory():
            cpe = software.get('cpe')
            if cpe is not None:
                value = cpe.get('wfn').get(attribute)
                if value not in values:
                    values.append(value)
        return values


class Software:

    def __init__(self, new_software):
        self.new_software = new_software
        self.update_software_document()

    def get(self):
        return self.new_software

    def get_id(self):
        return self.new_software.get('id')

    def update_software_document(self):
        self.new_software['id'] = generate_software_id(self.new_software)
        self.new_software['cpe'] = None
        self.new_software['cve_matches'] = []


def sort_software_products_by_vendor(sw_products):
    ordered_sw_products = []
    none = []
    ubuntu = []
    others = []
    microsoft = []
    for software in sw_products:
        if is_software_vendor_microsoft(software):
            microsoft.append(software)
        elif is_software_vendor_ubuntu(software):
            ubuntu.append(software)
        elif is_software_vendor_none(software):
            none.append(software)
        else:
            others.append(software)
    ordered_sw_products.extend(microsoft)
    ordered_sw_products.extend(others)
    ordered_sw_products.extend(ubuntu)
    ordered_sw_products.extend(none)
    return ordered_sw_products


def is_software_vendor_microsoft(software):
    return 'microsoft' in str.lower(str(software.get('vendor')))


def is_software_vendor_ubuntu(software):
    return 'ubuntu' in str.lower(str(software.get('vendor')))


def is_software_vendor_none(software):
    return software.get('vendor') is None


def generate_software_id(software):
    return generate_md5(generate_software_id_seed(software))


def generate_md5(seed):
    return hashlib.md5(str.encode(seed)).hexdigest()


def generate_software_id_seed(item):
    return str(item.get('product')) + str(item.get('vendor')) + str(item.get('version'))


def has_cpe(software):
    return software.get('cpe') is not None
