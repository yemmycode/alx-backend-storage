#!/usr/bin/env python3
'''Task 11: Python Learning Resources
'''

def schools_by_topic(mongo_collection, topic):
    '''Fetches a list of schools that offer a given topic.
    '''
    topic_filter = {
        'topics': {
            '$elemMatch': {
                '$eq': topic,
            },
        },
    }
    return [doc for doc in mongo_collection.find(topic_filter)]
