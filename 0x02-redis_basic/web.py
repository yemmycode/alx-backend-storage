#!/usr/bin/env python3
'''Module for caching and tracking HTTP request data.
'''
import redis
import requests
from functools import wraps
from typing import Callable


# Initialize a Redis instance for the module
redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    '''Decorator that caches the result of the data fetched by the method.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''Wrapper function that handles caching and counting requests for the given URL.
        '''
        # Increment the access count for the URL
        redis_store.incr(f'count:{url}')
        
        # Check if the result is already cached
        cached_result = redis_store.get(f'result:{url}')
        if cached_result:
            return cached_result.decode('utf-8')
        
        # Fetch the result using the decorated method and cache it
        fetched_result = method(url)
        redis_store.set(f'count:{url}', 0)  # Reset the counter after fetching
        redis_store.setex(f'result:{url}', 10, fetched_result)  # Cache the result with expiration
        return fetched_result
    
    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Fetches the content of the specified URL, caches the response, and tracks its access.
    '''
    return requests.get(url).text
