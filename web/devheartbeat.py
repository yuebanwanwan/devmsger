#!/usr/bin/env python
#encoding=utf-8

import time
import threading
from settings import api_settings
from redismsger import msger

class DevHeartbeat(threading.Thread):
    """ 客户端 到采数软件的定时心跳包  """
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            time.sleep(api_settings.HEARTBEAT)
            msger.publish('Heartbeat', 'client -> server')
