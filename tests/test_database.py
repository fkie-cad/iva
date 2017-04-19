import unittest
from copy import copy
from tests.dict_tester import DictTester
from pymongo import MongoClient
from tests.mock_config import *

COLLECTION_NAME = 'test_collection'
DOC = {'wfn': {'part': 'a', 'vendor': '$0.99_kindle_books_project', 'product': '$0.99_kindle_books', 'version': '6',
               'update': 'ANY', 'edition': 'ANY', 'sw_edition': 'ANY', 'target_sw': 'android', 'target_hw': 'ANY',
               'other': 'ANY', 'language': 'ANY'},
       'uri_binding': 'test_cpe:/a:%240.99_kindle_books_project:%240.99_kindle_books:6::~~~android~~',
       'formatted_string_binding': 'test_cpe:2.3:a:\$0.99_kindle_books_project:\$0.99_kindle_books:6:*:*:*:*:android:*:*'
       }
DOCUMENTS = [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}, {'id': 6}, {'id': 7}, {'id': 8}, {'id': 9},
             {'id': 10}, {'id': 11}, {'id': 12}]

CVE_1 = {'cve_id': 'CVE-2017-0004', 'cve_summary': 'blablbablablaabla.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:adobe:adobe_reader:9.5',
                          'wfn': {'vendor': 'adobe', 'product': 'adobe_reader'}},
                         {'uri_binding': 'cpe:/a:adobe:reader:9.5',
                          'wfn': {'vendor': 'adobe', 'product': 'reader'}},
                         {'uri_binding': 'cpe:/a:bla:blabla:111',
                          'wfn': {'vendor': 'no_adobe', 'product': 'adobe_reader'}}]}

CVE_2 = {'cve_id': 'CVE-2017-0005', 'cve_summary': 'blablbablablaabla.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:adobe:reader:4525',
                          'wfn': {'vendor': 'adobe', 'product': 'reader'}},
                         {'uri_binding': 'cpe:/a:bla:blabla:111',
                          'wfn': {'vendor': 'no_adobe', 'product': 'adobe_reader'}}]}

CVE_3 = {'cve_id': 'CVE-2017-0006', 'cve_summary': 'blablbablablaabla.',
         'cpe_entries': [{'uri_binding': 'cpe:/a:microsoft:ie:11',
                          'wfn': {'vendor': 'microsoft', 'product': 'ie'}},
                         {'uri_binding': 'cpe:/a:mozilla:firefox:40',
                          'wfn': {'vendor': 'adobe', 'mozilla': 'firefox'}}]}


class TestDatabase(unittest.TestCase):

    def setUp(self):
        # mock
        self.dict_tester = DictTester()
        self.mongodb_client = MongoClient(DB_HOST, DB_PORT)
        self.test_db = self.mongodb_client[IVA_DB_NAME]
        self.test_db_collection = self.test_db[COLLECTION_NAME]
        self.create_db_object()

    def create_db_object(self):
        self.db = patch_config_for('database', 'Database')

    def test_insert_doc_into_collection(self):
        # insert document
        self.db.insert_document_in_collection(DOC, COLLECTION_NAME)

        # verify insert
        self.assertTrue(IVA_DB_NAME in self.mongodb_client.database_names(), 'Database ' + IVA_DB_NAME + ' was not created')
        self.assertTrue(COLLECTION_NAME in self.test_db.collection_names(), 'Collection ' + COLLECTION_NAME + ' was not created')
        self.assertIsNotNone(self.test_db_collection.find_one(DOC), 'Document ' + str(DOC) + ' was not inserted')

    def test_exist_doc_in_collection_return_true(self):
        # insert document
        self.test_db_collection.insert_one(DOC)

        # search document
        self.assertTrue(self.db.exist_doc_in_collection({'uri_binding': DOC.get('uri_binding')}, COLLECTION_NAME))

    def test_search_text_in_collection_with_regex(self):
        # insert document
        self.test_db_collection.insert_one(DOC)

        # search
        regex = '^\$0\.99.*'
        field = 'wfn.vendor'
        search_result = self.db.search_text_with_regex_in_collection(regex, field, COLLECTION_NAME)
        # verify
        self.assertEqual(search_result.count(), 1)

        # search
        regex = 'kindle_books$'
        field = 'wfn.product'
        search_result = self.db.search_text_with_regex_in_collection(regex, field, COLLECTION_NAME)
        # verify
        self.assertEqual(search_result.count(), 1)

        # search
        regex = '^kindle_books$'
        field = 'wfn.product'
        search_result = self.db.search_text_with_regex_in_collection(regex, field, COLLECTION_NAME)
        # verify
        self.assertEqual(search_result.count(), 0)

        # search
        regex = '^\$0\.99.*books$'
        field = 'wfn.product'
        search_result = self.db.search_text_with_regex_in_collection(regex, field, COLLECTION_NAME)
        # verify
        self.assertEqual(search_result.count(), 1)

    def test_search_text_in_collection_with_regex_does_not_find_matches_when_special_chars_not_escaped(self):
        # insert document
        self.test_db_collection.insert_one(DOC)

        # search document
        regex = '^$0.99.*'
        field = 'wfn.vendor'
        search_result = self.db.search_text_with_regex_in_collection(regex, field, COLLECTION_NAME)
        # verify
        self.assertEqual(search_result.count(), 0)

    def test_exist_doc_in_collection_return_false(self):
        # search document
        self.assertFalse(self.db.exist_doc_in_collection({'uri_binding': DOC.get('uri_binding')}, COLLECTION_NAME))

    def test_number_of_documents_in_collection_returns_5(self):
        # insert 5 documents in collection
        for i in range(5):
            self.db.insert_document_in_collection({'id': i}, COLLECTION_NAME)

        # get number of documents in collection
        self.assertEqual(5, self.db.get_number_of_documents_in_collection(COLLECTION_NAME))

    def test_number_of_documents_in_collection_returns_0(self):
        # get number of documents in collection
        self.assertEqual(0, self.db.get_number_of_documents_in_collection(COLLECTION_NAME))

    def test_number_of_documents_with_filter_returns_3(self):
        self.db.insert_document_in_collection({'id': '1', 'status': 'new'}, COLLECTION_NAME)
        self.db.insert_document_in_collection({'id': '1', 'status': 'removed'}, COLLECTION_NAME)
        self.db.insert_document_in_collection({'id': '2', 'status': 'new'}, COLLECTION_NAME)
        self.db.insert_document_in_collection({'id': '1', 'status': 'closed'}, COLLECTION_NAME)
        self.db.insert_document_in_collection({'id': '1', 'status': 'new'}, COLLECTION_NAME)

        # get number of documents in collection
        self.assertEqual(3, self.db.get_number_of_documents_in_collection(COLLECTION_NAME, {'status': 'new'}))

    def test_number_of_documents_with_filter_returns_0(self):
        self.db.insert_document_in_collection({'id': '1', 'status': 'new'}, COLLECTION_NAME)
        self.db.insert_document_in_collection({'id': '1', 'status': 'removed'}, COLLECTION_NAME)
        self.db.insert_document_in_collection({'id': '2', 'status': 'closed'}, COLLECTION_NAME)

        # get number of documents in collection
        self.assertEqual(0, self.db.get_number_of_documents_in_collection(COLLECTION_NAME, {'status': 'any'}))

    def test_update_document_in_collection(self):
        # insert document
        doc_to_be_updated = {'doc_id': 1, 'value': 'to be updated'}
        self.test_db_collection.insert_one(doc_to_be_updated)

        # update document
        filter_ = {'doc_id': 1}
        update = {'value': 'updated'}
        self.db.update_document_in_collection(filter_, update, COLLECTION_NAME)

        # verify update
        updated_doc = self.test_db_collection.find_one(filter_)
        self.assertIsNotNone(self.test_db_collection.find_one(updated_doc))
        self.assertEqual(updated_doc.get('value'), 'updated')

    def test_update_documents_in_collection(self):
        # insert document
        doc_to_be_updated = {'doc_id': 1, 'value': 'to be updated'}
        self.test_db_collection.insert_one(doc_to_be_updated)

        docs = [{'doc_id': 1, 'value': 'updated'},
                {'doc_id': 2, 'value': 'new inserted'}]
        find_filter = 'doc_id'
        self.db.update_documents_in_collection(docs, find_filter, COLLECTION_NAME)

        # verify update
        self.assertEqual(2, self.test_db_collection.count())
        updated_doc = self.test_db_collection.find_one({'doc_id': 1})
        self.assertEqual(updated_doc.get('value'), 'updated')
        inserted_doc = self.test_db_collection.find_one({'doc_id': 2})
        self.assertEqual(inserted_doc.get('value'), 'new inserted')

    def test_update_documents_in_collection_when_doc_list_empty(self):
        self.db.update_documents_in_collection([], '', COLLECTION_NAME)

    def test_search_doc_in_collection_returns_one_dict(self):
        search_condition = {'test_name': 'search_doc_in_collection'}

        # insert document
        self.test_db_collection.insert_one({'id_test': '1', 'test_name': 'search_doc_in_collection'})

        # search document
        dict_ = self.db.search_document_in_collection(search_condition, COLLECTION_NAME)

        # verify
        self.dict_tester.assertEqualKeys({'id_test': '1', 'test_name': 'search_doc_in_collection'}, dict_)
        self.dict_tester.assertEqualValues({'id_test': '1', 'test_name': 'search_doc_in_collection'}, dict_)

    def test_search_doc_in_collection_returns_one_dict_without_id_attribute(self):
        search_condition = {'test_name': 'search_doc_in_collection'}
        expected_dict = {'i': '1', 'test_name': 'search_doc_in_collection'}

        # insert document
        self.test_db_collection.insert_one(expected_dict)

        # search document
        dict_ = self.db.search_document_in_collection(search_condition, COLLECTION_NAME)

        # verify
        self.assertFalse('_id' in dict_)

    def test_search_doc_with_array_in_collection_returns_one_dict(self):
        search_condition = {'tests': {'$in': ['test2']}}
        expected_dict = {'id_test': '1', 'tests': ['search_doc_in_collection', 'test2']}

        # insert document
        self.test_db_collection.insert_one(copy(expected_dict))

        # search document
        dict_ = self.db.search_document_in_collection(search_condition, COLLECTION_NAME)

        # verify
        self.dict_tester.assertEqualKeys(expected_dict, dict_)
        self.dict_tester.assertEqualValues(expected_dict, dict_)

    def test_search_array_nested_doc_with_array_in_collection_returns_one_dict(self):
        search_condition = {'tests': {'$elemMatch': {'test_name': 'test2'}}}
        expected_dict = {'id_test': '1', 'tests': [{'test_name': 'search_doc_in_collection'},
                                                   {'test_name': 'test2'}]}

        # insert document
        self.test_db_collection.insert_one(copy(expected_dict))

        # search document
        dict_ = self.db.search_document_in_collection(search_condition, COLLECTION_NAME)

        # verify
        self.dict_tester.assertEqualKeys(expected_dict, dict_)
        self.dict_tester.assertEqualValues(expected_dict, dict_)

    def test_search_doc_in_collection_returns_none(self):
        search_condition = {'test_name': 'not_found'}
        expected_dict = {'id_test': '1', 'test_name': 'search_doc_in_collection'}

        # insert document
        self.test_db_collection.insert_one(expected_dict)

        # search document
        dict_ = self.db.search_document_in_collection(search_condition, COLLECTION_NAME)

        # verify
        self.assertIsNone(dict_)

    def test_get_documents_from_collection(self):
        self.test_db_collection.insert_many(documents=[{'id_doc': 1}, {'id_doc': 2}, {'id_doc': 3}, {'id_doc': 4}])

        # get documents
        docs = self.db.get_documents_from_collection(COLLECTION_NAME)

        # verify
        self.assertEqual(4, len(docs))
        self.assertEqual({'id_doc': 1}, docs[0])
        self.assertEqual({'id_doc': 2}, docs[1])
        self.assertEqual({'id_doc': 3}, docs[2])
        self.assertEqual({'id_doc': 4}, docs[3])

    def test_delete_document_from_collection(self):
        # insert document to be deleted
        self.test_db_collection.insert_one({'id_doc': 1, 'text': 'this is a test'})

        # delete document
        self.db.delete_document_from_collection({'id_doc': 1}, COLLECTION_NAME)

        # verify
        self.assertIsNone(self.test_db_collection.find_one({'id_doc': 1}))

    def test_get_documents_from_collection_in_range_0_3(self):
        self.test_db_collection.insert_many(documents=DOCUMENTS)
        documents = self.db.get_documents_from_collection_in_range(COLLECTION_NAME, skip=0, limit=3)
        self.assertEqual(3, len(documents))
        self.assertEqual(DOCUMENTS[0].get('id'), documents[0].get('id'))
        self.assertEqual(DOCUMENTS[1].get('id'), documents[1].get('id'))
        self.assertEqual(DOCUMENTS[2].get('id'), documents[2].get('id'))

    def test_get_documents_from_collection_in_range_5_0(self):
        self.test_db_collection.insert_many(documents=DOCUMENTS)
        documents = self.db.get_documents_from_collection_in_range(COLLECTION_NAME, skip=5, limit=0)
        self.assertEqual(len(DOCUMENTS)-5, len(documents))
        self.assertEqual(DOCUMENTS[5].get('id'), documents[0].get('id'))
        self.assertEqual(DOCUMENTS[len(DOCUMENTS)-1].get('id'), documents[len(documents)-1].get('id'))

    def test_get_documents_from_collection_in_range_2_1(self):
        self.test_db_collection.insert_many(documents=DOCUMENTS)
        documents = self.db.get_documents_from_collection_in_range(COLLECTION_NAME, skip=2, limit=1)
        self.assertEqual(1, len(documents))
        self.assertEqual(3, documents[0].get('id'))

    def test_get_documents_from_collection_in_range_0_0_returns_all_documents(self):
        self.test_db_collection.insert_many(documents=DOCUMENTS)
        documents = self.db.get_documents_from_collection_in_range(COLLECTION_NAME, skip=0, limit=0)
        self.assertEqual(len(DOCUMENTS), len(documents))

    def test_aggregation(self):
        self.test_db_collection.insert_many(documents=[CVE_1, CVE_2, CVE_3])
        # search condition is met in one document
        search_condition = {'cpe_entries': {'$elemMatch': {'$and': [{'wfn.product': 'adobe_reader'}, {'wfn.vendor': 'adobe'}]}}}
        aggregation_filter_ = {'input': '$cpe_entries', 'as': 'cpe_entries',
                               'cond': {'$and': [{'$eq': ['$$cpe_entries.wfn.product', 'adobe_reader']},
                                                 {'$eq': ['$$cpe_entries.wfn.vendor', 'adobe']}]}}
        aggregation = {'cpe_entries': {'$filter': aggregation_filter_}, '_id': 0, 'cve_id': 1, 'cve_summary': 1}
        documents = self.db.search_documents_and_aggregate(search_condition, aggregation, COLLECTION_NAME)
        self.assertEqual(1, len(documents))
        cpe_entries = documents[0].get('cpe_entries')
        self.assertEqual(1, len(cpe_entries))
        wfn = cpe_entries[0].get('wfn')
        self.assertEqual('adobe_reader', wfn.get('product'))
        self.assertEqual('adobe', wfn.get('vendor'))

        # search condition is met in two documents
        search_condition = {'$and': [{'cpe_entries.wfn.product': 'reader'}, {'cpe_entries.wfn.vendor': 'adobe'}]}
        aggregation_filter_ = {'input': '$cpe_entries', 'as': 'cpe_entries',
                               'cond': {'$and': [{'$eq': ['$$cpe_entries.wfn.product', 'reader']},
                                                 {'$eq': ['$$cpe_entries.wfn.vendor', 'adobe']}]}}
        aggregation = {'cpe_entries': {'$filter': aggregation_filter_}, '_id': 0, 'cve_id': 1, 'cve_summary': 1}
        documents = self.db.search_documents_and_aggregate(search_condition, aggregation, COLLECTION_NAME)
        self.assertEqual(2, len(documents))

        # search condition is not met
        search_condition = {'$and': [{'cpe_entries.wfn.product': 'reader__'}, {'cpe_entries.wfn.vendor': '__adobe'}]}
        aggregation_filter_ = {'input': '$cpe_entries', 'as': 'cpe_entries',
                               'cond': {'$and': [{'$eq': ['$$cpe_entries.wfn.product', 'reader']},
                                                 {'$eq': ['$$cpe_entries.wfn.vendor', 'adobe']}]}}
        aggregation = {'cpe_entries': {'$filter': aggregation_filter_}, '_id': 0, 'cve_id': 1, 'cve_summary': 1}
        documents = self.db.search_documents_and_aggregate(search_condition, aggregation, COLLECTION_NAME)
        self.assertEqual(0, len(documents))


    def tearDown(self):
        self.db.close()
        self.mongodb_client.drop_database(IVA_DB_NAME)
        self.mongodb_client.close()

if __name__ == '__main__':
    unittest.main()
