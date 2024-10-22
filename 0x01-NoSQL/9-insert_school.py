#!/usr/bin/env python3
'''Task 9: Adding a document using Python
'''

def insert_school(mongo_collection, **kwargs):
    '''Adds a new document to the specified collection.
    '''
    result = mongo_collection.insert_one(kwargs)
    return result.inserted_id
