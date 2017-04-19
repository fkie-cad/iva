from pymongo import MongoClient
import config


class Database:

    def __init__(self, db_name=None):
        self.mongodb_client = create_mongodb_client()
        self.db = self.create_db(db_name)
        self.authenticate_user()

    def create_db(self, db_name):
        if db_name is None:
            return self.mongodb_client[config.get_database_name()]
        return self.mongodb_client[db_name]

    def authenticate_user(self):
        if config.is_database_authentication_enabled():
            self.db.authenticate(config.get_database_user(), config.get_database_password())

    def insert_document_in_collection(self, doc, collection_name):
        collection = self.db[collection_name]
        collection.insert_one(doc)

    def exist_doc_in_collection(self, search_condition, collection_name):
        collection = self.db[collection_name]
        query_result = collection.find(search_condition).limit(1)
        return doc_found(query_result)

    def search_text_with_regex_in_collection(self, regex, field, collection_name):
        collection = self.db[collection_name]
        return collection.find({field: get_regex_dict(regex)})

    def search_text_with_regex_in_collection_mul(self, regex_a, regex_b, field_a, field_b, collection_name):
        collection = self.db[collection_name]
        return collection.find({'$and': [{field_a: get_regex_dict(regex_a)}, {field_b: get_regex_dict(regex_b)}]})

    def search_document_in_collection(self, search_condition, collection_name):
        collection = self.db[collection_name]
        return collection.find_one(search_condition, {'_id': 0})

    def search_documents_in_collection(self, search_condition, collection_name):
        collection = self.db[collection_name]
        return collection.find(search_condition, {'_id': 0})

    def search_documents_and_aggregate(self, search_condition, aggregation, collection_name):
        collection = self.db[collection_name]
        return list(collection.aggregate([{'$match': search_condition}, {'$project': aggregation}]))

    def get_number_of_documents_in_collection(self, collection_name, filter_=None):
        collection = self.db[collection_name]
        return collection.count(filter_)

    def update_document_in_collection(self, filter_, update, collection_name, insert_if_not_exists=False):
        collection = self.db[collection_name]
        collection.update_one(filter_, {'$set': update}, upsert=insert_if_not_exists)

    def update_documents_in_collection(self, docs, find_filter, collection_name):
        if len(docs) > 0:
            bulk = self.db[collection_name].initialize_ordered_bulk_op()
            for doc in docs:
                bulk.find({find_filter: doc.get(find_filter)}).upsert().update({'$set': doc})
            bulk.execute()

    def get_documents_from_collection(self, collection_name):
        collection = self.db[collection_name]
        return list(collection.find({}, {'_id': 0}))

    def get_documents_from_collection_in_range(self, collection_name, skip=0, limit=0):
        collection = self.db[collection_name]
        return list(collection.find({}, {'_id': 0}).skip(skip).limit(limit))

    def delete_document_from_collection(self, query, collection_name):
        collection = self.db[collection_name]
        collection.delete_one(query)

    def close(self):
        self.mongodb_client.close()

    def drop_collection(self, collection_name):
        collection = self.db[collection_name]
        collection.drop()

    def insert_documents_in_collection(self, documents, collection_name):
        collection = self.db[collection_name]
        collection.insert_many(documents=documents)

def create_mongodb_client():
    return MongoClient(config.get_database_host(), config.get_database_port())


def doc_found(query_result):
    found = query_result.count() > 0
    query_result.close()
    return found


def get_regex_dict(regex):
    return {'$regex': regex}