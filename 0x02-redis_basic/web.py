#!/usr/bin/env python3
'''This module provides utilities for caching HTTP request results and tracking their usage.
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_cache = redis.Redis()
'''Redis instance used to store cached data and track request counts.
'''


def cache_requests(method: Callable) -> Callable:
    '''Decorator that caches the response of HTTP requests and tracks how often they are made.
    '''
    @wraps(method)
    def wrapper(url: str) -> str:
        '''Caches the result of the given method and tracks the number of times a URL is accessed.
        '''
        redis_cache.incr(f'request_count:{url}')
        cached_result = redis_cache.get(f'cached_result:{url}')
        if cached_result:
            return cached_result.decode('utf-8')
        response = method(url)
        redis_cache.set(f'request_count:{url}', 0)
        redis_cache.setex(f'cached_result:{url}', 10, response)
        return response
    return wrapper


@cache_requests
def get_page(url: str) -> str:
    '''Fetches the content of the specified URL, caches the response, and tracks the request count.
    '''
    return requests.get(url).text
