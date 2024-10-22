#!/usr/bin/env python3
'''Task 10: Modify School Subjects
'''

def update_topics(mongo_collection, name, topics):
    '''Updates all topics in a document of the collection based on the specified name.
    '''
    mongo_collection.update_many(
        {'name': name},
        {'$set': {'topics': topics}}
    )
