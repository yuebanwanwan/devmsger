#!/usr/bin/env python
#encoding=utf-8

import redis
from settings import api_settings    
    
class RedisMsger(object):
    def __init__(self):
        self._redis_pub = redis.StrictRedis(api_settings.DEDIS_HOST, api_settings.DEDIS_PORT, db=0)
        
    def publish(self, channel, message):
        self._redis_pub.publish(channel, message)
        
    def set(self, key, value):
        self._redis_pub.set(key, value)
        
    def get(self, key):
        self._redis_pub.get(key)

msger = RedisMsger()