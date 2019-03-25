#!/usr/bin/env python
# encoding=utf-8

import time
import binascii
import threading
from socket import socket, AF_INET, SOCK_STREAM
from settings import api_settings
from utils import Converter

from redismsger import msger
from crc import get_crc16

from parsers import HeartbeatParser, RemoteExecutionParser, RemoteUndoParser, RealtimeDataParser, ParsePhoto
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

    # 和服务器建立连接
    def _connect(self):
        try:
            # AF_INET 基于网络的IPv4的套接字类型
            # SOCK_STREAM 套接字是基于IP协议的(一种无连接的网络通信协议)
            self._tcpCliSock = socket(AF_INET, SOCK_STREAM)
            # 主动发起TCP服务器连接(参数为服务器地址HOST加端口PORT)
            self._tcpCliSock.connect(
                (api_settings.PHOTO_SOFT_HOST, api_settings.PHOTO_SOFT_PORT))
            self.setConnectState(True)
        except Exception as ex:
            self.setConnectState(False)
            print u'!!!socket 客户端连接通讯服务器失败，可能通讯服务器软件并未运行或监听端口改变了'

    def run(self):
        print 'is run'
        photo_data = []

        def receive_msg():
            print 'is receive_msg'

            # 发送指令
            while True:
                if not self.connect_state:
                    time.sleep(1)
                    continue
                # send_message = '7E7E' + '0010000473' + '16' + '04D2' + '36' + '8008' + '02' + '0000' + '190118160607' + '05'
                self.send(self._get_instructions())
                print 'receive ing...'
                break

            # 获取数据
            data_list = []
            while True:
                data = self._tcpCliSock.recv(1024)
                data = data.encode('hex')
                data_list.append(data)
                if data[-6:-4] == '03':
                    break

            data_list = sorted(data_list, key=lambda x: int(x[31:34], 16))
            self.write_data(data_list)

            # photo_data = []
            for data in data_list:
                if not self.connect_state:
                    time.sleep(1)
                    continue
                if not data:
                    self.setConnectState(False)
                    print u'!!!通讯服务器主动断开连接'
                    # 当无法从服务器接受TCP消息时则会一直尝试获取TCP消息
                    continue

                function_code = self._get_function_code(data)

                if function_code != 54:
                    print u'数据包功能码无效: %s' % (function_code)

                parser = ParsePhoto()
                result = parser.parse(data)
                photo_data.append(result)
                if result is None:
                    print u'数据包crc无效：%s' % (self._get_hexstr(data))
                    continue

            self._write_to_picture(photo_data)


            # for data in Converter.get_data_lst():
            #     if not self.connect_state:
            #         time.sleep(1)
            #         continue
            #     try:
            #         # data = self._tcpCliSock.recv(1024)
            #         # 生产环境中的数据包都是没有空格符的
            #         # data = data.encode('hex')
            #
            #         if not data:
            #             self.setConnectState(False)
            #             print u'!!!通讯服务器主动断开连接'
            #             # 当无法从服务器接受TCP消息时则会一直尝试获取TCP消息
            #             continue
            #
            #         function_code = self._get_function_code(data)
            #
            #         if function_code != 54:
            #             print u'数据包功能码无效: %s' % (function_code)
            #
            #         parser = ParsePhoto()
            #         result = parser.parse(data)
            #         photo_data.append(result)
            #         if result is None:
            #             print u'数据包crc无效：%s' % (self._get_hexstr(data))
            #             continue
            #
            #     except Exception, e:
            #         print u'!!!devsocket run: %s ' % e.message
            #
            # self._write_to_picture(photo_data)

        subthread = threading.Thread(target=receive_msg, args=())
        subthread.start()

    def send(self, data):
        try:
            self._tcpCliSock.send(data)
        except Exception, e:
            # 若出现异常则关闭连接开关
            self.setConnectState(False)
            # 关闭套接字
            self.close()
            # 初始化套接字连接
            self._connect()
            print u'!!!socket send except:%s' % e

    def _get_instructions(self):
        """根据当前时间生成动态拍照指令(动态时间)
        """
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        date = current_time[2:4] + current_time[5:7] + current_time[8:10]
        hour = current_time[11:13] + current_time[14:16] + current_time[17:19]
        date = date + hour
        print 'date', date
        instruction = '7E7E0010000473160000368008020001' + date + '05'
        instruction = get_crc16(instruction)
        return instruction.decode('hex')

    def listen(self):
        # 调用父类的方法运行线程
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
        # 取功能🐎
        frameHead = hexstr[:2]
        cmd = hexstr[10:12]
        return int(frameHead, 16), int(cmd, 16)

    def _get_function_code(self, data):
        """取出照片数据中的功能码转化为十进制整数返回
        """
        # hexstr = self._get_hexstr(data)
        hexstr = data
        # 取出功能码
        function_code = hexstr[20:22]
        print 'function_code', function_code
        return int(function_code, 16)

    def _write_to_picture(self, data):
        datas = sorted(data, key=lambda x: x['current_order'])
        try:
            with open('test2.jpg', 'wb') as f:
                for data in datas:
                    f.write(data['data'].decode('hex'))
        except Exception as e:
            print u'写入文件时错误:%s' % (e.message)

    def write_data(self, datas):
        try:
            with open('data_list.txt', 'w') as f:
                for data in datas:
                    f.write(data + '\n')
        except Exception as e:
            print u'写入文件时错误:%s' % (e.message)

