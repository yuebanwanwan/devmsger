#!/usr/bin/env python
#encoding=utf-8

import threading
import redis

from settings import api_settings
from negotiation import ParserNegotiation
from parsers import HeartbeatSocketParser, RemoteExecutionSocketParser, UndoRemoteExecutionSocketParser

class HSRedis(threading.Thread):
    parser_classes = (HeartbeatSocketParser, RemoteExecutionSocketParser, UndoRemoteExecutionSocketParser)
    parser_negotiation = ParserNegotiation()
    
    def __init__(self, sendMsgToDev, *args, **kwargs):
        threading.Thread.__init__(self)
        
        self._redis = redis.StrictRedis(api_settings.DEDIS_HOST, api_settings.DEDIS_PORT, db = 0)
        self._pubsub = self._redis.pubsub()
        
        self._subscribe('Heartbeat')  # 心跳包
        self._subscribe('RemoteExecution') # 远程控制
        self._subscribe('UndoRemoteExecution') # 撤销远程控制
        
        self._devSocket = sendMsgToDev
        
    def run(self):
        for item in self._pubsub.listen():
            print item
            try:
                r_channel = item.get('channel', None)
                r_type = item.get('type', None)
                r_data = item.get('data', None)
                
                parser = self.parser_negotiation.select_parser(r_channel, r_type, self.parser_classes)
                if parser is None:
                    continue
                
                if r_data is not None:
                    result = parser.parse(r_data)
                    self._sendSocket(result)
            except Exception, e:
                print u'!!!hsredis run:%s' % e
            
    def _sendSocket(self, data):
        try:
            self._devSocket.send(data)
        except Exception:
            raise Exception(u'向通讯服务器发送数据失败。')
            
    def _subscribe(self, channel):
        self._pubsub.subscribe(channel)
        
    def listen(self):
        self.start()