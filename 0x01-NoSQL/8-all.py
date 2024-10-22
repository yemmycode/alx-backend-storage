#!/usr/bin/env python3
"""Module for Task 8.
"""

def list_all(mongo_collection):
    """Retrieves all documents from a specified collection.
    """
    return [doc for doc in mongo_collection.find()]
