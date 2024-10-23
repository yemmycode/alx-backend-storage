#!/usr/bin/env python3
'''This module facilitates interaction with the Redis NoSQL database.
'''
from functools import wraps
from typing import Any, Callable, Union
import redis
import uuid


def track_call_count(method: Callable) -> Callable:
    '''Counts how many times a method in the Cache class is called.
    '''
    @wraps(method)
    def wrapped(self, *args, **kwargs) -> Any:
        '''Increments the call counter for the method before executing it.
        '''
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapped


def track_call_history(method: Callable) -> Callable:
    '''Records the input and output history of a method in the Cache class.
    '''
    @wraps(method)
    def wrapped_with_history(self, *args, **kwargs) -> Any:
        '''Stores the method's arguments and return value.
        '''
        input_key = '{}:inputs'.format(method.__qualname__)
        output_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, result)
        return result
    return wrapped_with_history


def display_history(fn: Callable) -> None:
    '''Prints the recorded input/output history for a method in Cache.
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_instance = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_instance, redis.Redis):
        return
    method_name = fn.__qualname__
    input_key = '{}:inputs'.format(method_name)
    output_key = '{}:outputs'.format(method_name)
    call_count = 0
    if redis_instance.exists(method_name) != 0:
        call_count = int(redis_instance.get(method_name))
    print('{} was called {} times:'.format(method_name, call_count))
    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)
    for input_val, output_val in zip(inputs, outputs):
        print('{}(*{}) -> {}'.format(
            method_name,
            input_val.decode("utf-8"),
            output_val,
        ))


class Cache:
    '''Represents a caching system that interfaces with Redis for data storage.
    '''

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @track_call_history
    @track_call_count
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Saves a value in Redis and returns the key used to access it.
        '''
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def retrieve(
            self,
            key: str,
            transform: Callable = None,
            ) -> Union[str, bytes, int, float]:
        '''Fetches a value from Redis and optionally applies a transformation.
        '''
        value = self._redis.get(key)
        return transform(value) if transform is not None else value

    def retrieve_str(self, key: str) -> str:
        '''Fetches a value from Redis and returns it as a string.
        '''
        return self.retrieve(key, lambda x: x.decode('utf-8'))

    def retrieve_int(self, key: str) -> int:
        '''Fetches a value from Redis and returns it as an integer.
        '''
        return self.retrieve(key, lambda x: int(x))
