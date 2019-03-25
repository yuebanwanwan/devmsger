#!/usr/bin/env python
# encoding=utf-8

import time
import binascii
import threading
from socket import socket, AF_INET, SOCK_STREAM
from settings import api_settings

from redismsger import msger

from parsers import HeartbeatParser, RemoteExecutionParser, RemoteUndoParser, RealtimeDataParser
from negotiation import ParserNegotiation


class PhotoSocket(threading.Thread):
    parser_classes = (HeartbeatParser, RemoteExecutionParser,
                      RemoteUndoParser, RealtimeDataParser)
    parser_negotiation = ParserNegotiation()

    def __init__(self, *args, **kwargs):
        # super(PhotoSocket, self).__init__()
        threading.Thread.__init__(self)
        self.connect_state = False
        self._connect()

    def _connect(self):
        try:
            self._tcpCliSock = socket(AF_INET, SOCK_STREAM)
            self._tcpCliSock.connect(
                (api_settings.PHOTO_SOFT_HOST, api_settings.PHOTO_SOFT_PORT))
            self.setConnectState(True)
        except Exception as ex:
            self.setConnectState(False)
            print u'!!!socket 客户端连接通讯服务器失败，可能通讯服务器软件并未运行或监听端口改变了'

    def run(self):
        print 'is run'

        def receive_msg():
            print 'is receive_msg'

            while True:
                if not self.connect_state:
                    time.sleep(1)
                    continue

                self.send(u'0x7E7E00100004731604D23680080200011901161800000536F5')
                print 'receive ing...'
                try:
                    data = self._tcpCliSock.recv(1024)
                    print type(data)
                    print data
                except Exception, e:
                    print u'!!!devsocket run: %s ' % e

            while True:
                if not self.connect_state:
                    time.sleep(1)
                    continue

                try:
                    data = self._tcpCliSock.recv(1024)
                    print data
                    print type(data)
                    if not data:
                        self.setConnectState(False)
                        print u'!!!通讯服务器主动断开连接'
                        continue
                    frameHead, cmd = self._get_frameHead_cmd(data)
                    parser = self.parser_negotiation.select_parser(
                        frameHead, cmd, self.parser_classes)

                    if parser is None:
                        print u'数据包的帧头或命令帧无效：%s' % (self._get_hexstr(data))
                        continue

                    result = parser.parse(data)
                    if result is None:
                        print u'数据包crc无效：%s' % (self._get_hexstr(data))
                        continue

                    if isinstance(result, dict):
                        msger.publish(result['channel'], result['message'])
                    elif isinstance(result, list):
                        for item in result:
                            msger.publish(item['channel'], item['message'])
                except Exception, e:
                    print u'!!!devsocket run: %s ' % e

        subthread = threading.Thread(target=receive_msg, args=())
        subthread.start()

    def send(self, data):
        try:
            self._tcpCliSock.send(data)
        except Exception, e:
            self.setConnectState(False)
            self.close()
            self._connect()
            print u'!!!socket send except:%s' % e

    def listen(self):
        self.start()

    def close(self):
        self._tcpCliSock.close()

    def _get_hexstr(self, data):
        hexstr = binascii.hexlify(data)
        return hexstr

    def setConnectState(self, state):
        self.connect_state = state
        # msger.set('devmsger_connect_state', state)

    def _get_frameHead_cmd(self, data):
        hexstr = self._get_hexstr(data)
        frameHead = hexstr[:2]
        cmd = hexstr[10:12]
        return int(frameHead, 16), int(cmd, 16)

    def _get_function_code(self, data):
        """取出照片数据中的功能码转化为十进制整数返回
        """
        hexstr = self._get_hexstr(data)
        function_code = hexstr[20:22]
        return int(function_code, 16)

