#!/usr/bin/env python
#encoding=utf-8

'''
Created on 2016-3-26
@author: cdhongsheng.com
'''

import json
import struct
import binascii
from crc import crc16, get_crc16, get_int_array
from web.my_crc import Crc16

class SocketParser(object):
    """用于解析服务端通过socket发送的数据帧"""
    frameHead = 0xdf
    cmd_type = None
    
    def parse(self, data):
        raise NotImplementedError(".parse() must be overridden.")
    
    def crc16_check(self, data):
        hexstr = binascii.hexlify(data)
        frameLen = int(hexstr[2:6], 16)
        s1 = struct.Struct('!' + str(frameLen - 2) + 'B')
        s2 = struct.Struct('!H')
        pchMsg = s1.unpack_from(data, 0)
        _crc = s2.unpack_from(data, s1.size)[0]
        return crc16(pchMsg) == _crc
    
class HeartbeatParser(SocketParser):
    """socket心跳包解析"""
    cmd_type = 0x99
    
    def parse(self, data):
        if not self.crc16_check(data):
            return None
        return {'channel': 'Heartbeat', 'message': 'server -> client'}
        
class RemoteExecutionParser(SocketParser):
    """远程控制回执状态解析，发送遥控命令后服务端返回改设备是否可控"""
    cmd_type = 0xaa
    
    def parse(self, data):
        if not self.crc16_check(data):
            return None
        
        print u'RemoteExecutionParser?'                    
        print u'Hex:', binascii.hexlify(data)
        s1 = struct.Struct('!B2H4B')
        s2 = struct.Struct('<I')
        s3 = struct.Struct('!H')
        frameHead, frameLen, userId, cmd, systemId, deviceId, sensorId = s1.unpack_from(data, 0)
        value = s2.unpack_from(data, s1.size)[0]
        crc16 = s3.unpack_from(data, s2.size)[0]
        text = u'frameHead:%s,frameLen:%s,userId:%s,cmd:%s,systemId:%s,deviceId:%s,sensorId:%s,value:%s,crc16:%s' % (frameHead, frameLen, userId, cmd, systemId, deviceId, sensorId, value, crc16)
        print u'Parser:', text
        return {'channel': 'RemoteExecutionReceipt', 'message': json.dumps({'System_Id': systemId, 'Device_Id': deviceId, 'Sensor_Id': sensorId, 'Value': value})}

class RemoteUndoParser(RemoteExecutionParser):
    """撤销远程控制回执状态解析，发送撤销遥控命令后服务端返回改设备是否撤销"""
    cmd_type = 0x55
    
class RealtimeDataParser(SocketParser):
    """实时数据解析，发送遥控指令后如果该闸门可控，则要将最新的该设备的最新数据返回，同时还包括状态传感器"""
    cmd_type = 0x21
    
    def parse(self, data):
        if not self.crc16_check(data):
            return None
        
        print u'RealtimeDataParser?'
        hexstr = binascii.hexlify(data)
        frameLen = int(hexstr[2:6], 16)
        count = (frameLen - 10) / 5
        s1 = struct.Struct('!BH3BHB')
        s2 = struct.Struct('<f')
        print u'Hex:', hexstr
        
        lst = []
        for i in range(count):
            newFrame = '%s%s' % (hexstr[0:16], hexstr[16 + i * 10: 16 + (i + 1) * 10])
            prebuffer = binascii.unhexlify(newFrame)
            frameHead, frameLen, systemId, deviceId, cmd, userId, sensorId = s1.unpack_from(prebuffer, 0)
            value = s2.unpack_from(prebuffer, s1.size)[0]
            text = u'frameHead:%s,frameLen:%s,userId:%s,cmd:%s,systemId:%s,deviceId:%s,sensorId:%s,value:%s' % (frameHead, frameLen, userId, cmd, systemId, deviceId, sensorId, value)
            print u'Parser:', text
            
            if sensorId == 162:
                valueInt = int(value)
                bitstr = '{0:032b}'.format(valueInt)
                d = {'System_Id': systemId, 'Device_Id': deviceId, 'Sensor_Id': sensorId, 'Value': valueInt, 
                    'BIT0': int(bitstr[31]), 'BIT1': int(bitstr[30]), 'BIT2': int(bitstr[29]), 'BIT3': int(bitstr[28]), 
                    'BIT4': int(bitstr[27]), 'BIT5': int(bitstr[26]), 'BIT6': int(bitstr[25]), 'BIT7': int(bitstr[24]), 
                    'BIT8': int(bitstr[23]), 'BIT9': int(bitstr[22]), 'BIT10': int(bitstr[21]), 'BIT11': int(bitstr[20]), 
                    'BIT12': int(bitstr[19]), 'BIT13': int(bitstr[18]), 'BIT14': int(bitstr[17]), 'BIT15': int(bitstr[16]), 
                    'BIT16': int(bitstr[15]), 'BIT17': int(bitstr[14]), 'BIT18': int(bitstr[13]), 'BIT19': int(bitstr[12]), 
                    'BIT20': int(bitstr[11]), 'BIT21': int(bitstr[10]), 'BIT22': int(bitstr[9]), 'BIT23': int(bitstr[8]), 
                    'BIT24': int(bitstr[7]), 'BIT25': int(bitstr[6]), 'BIT26': int(bitstr[5]), 'BIT27': int(bitstr[4]), 
                    'BIT28': int(bitstr[3]), 'BIT29': int(bitstr[2]), 'BIT30': int(bitstr[1]), 'BIT31': int(bitstr[31])}
                lst.append({'channel': 'SensorRealtimeState', 'message': json.dumps(d)}) 
            else:
                d = {'System_Id': systemId, 'Device_Id': deviceId, 'Sensor_Id': sensorId, 'Value': "%.2f" % value}
                lst.append({'channel': 'SensorRealtimeData', 'message': json.dumps(d)})   
        return lst


class ParsePhoto(RealtimeDataParser):
    """解析拍照上传的每个分包的数据
    """
    function_type = 0x36

    def crc16_check(self, data):
        # 获取未添加校验码的原始报文
        information_code = data[:len(data) - 4]
        print u'information_code:', information_code
        return True if get_crc16(information_code) == data else False

    def parse(self, data):
        """data: hex格式字符串分包信息
        """
        origin_data = data
        # 校验crc时要将空格字符去掉
        crc_data = data[len(data) - 4:]
        # 获取包含未交换高低位校验码的报文
        data = data[:len(data) - 4] + crc_data[2:4] + crc_data[0:2]
        data_array = get_int_array(data)
        crc_16 = Crc16()
        if crc_16.calcrc(data_array) == 1:
            print u'crc校验码错误'
            return None
        print u'crc校验成功'

        # 获取分包总数(包总数在分包中的位置是固定的)
        sum_package = origin_data[28:31]
        # 获取当前包的序号(通过与分包总数可判断当前包是第一个或最后一个或中间的)
        current_order = origin_data[31:34]

        # 判断当前分包的位置
        if current_order == '001':
            # 第一个
            begin = 84
            # 获取包含图片数据的十六进制字符串
            package_data = origin_data[begin:len(origin_data) - 6]
        elif current_order == sum_package:
            # 最后一个包
            begin = 34
            package_data = origin_data[begin:len(origin_data) - 6]
        else:
            # 中间的包
            begin = 34
            package_data = origin_data[begin:len(origin_data) - 6]
        print u'current_order:', int(current_order, 16)
        print u'data:', package_data
        return {
            'current_order': int(current_order, 16),
            'data': package_data
        }






        print u'Realti  meDataParser?'
        hexstr = binascii.hexlify(data)
        hexstr = data
        frameLen = int(hexstr[2:6], 16)
        count = (frameLen - 10) / 5
        s1 = struct.Struct('!BH3BHB')
        s2 = struct.Struct('<f')
        print u'Hex:', hexstr

        lst = []
        for i in range(count):
            newFrame = '%s%s' % (hexstr[0:16], hexstr[16 + i * 10: 16 + (i + 1) * 10])
            prebuffer = binascii.unhexlify(newFrame)
            frameHead, frameLen, systemId, deviceId, cmd, userId, sensorId = s1.unpack_from(prebuffer, 0)
            value = s2.unpack_from(prebuffer, s1.size)[0]
            text = u'frameHead:%s,frameLen:%s,userId:%s,cmd:%s,systemId:%s,deviceId:%s,sensorId:%s,value:%s' % (
            frameHead, frameLen, userId, cmd, systemId, deviceId, sensorId, value)
            print u'Parser:', text

            if sensorId == 162:
                valueInt = int(value)
                bitstr = '{0:032b}'.format(valueInt)
                d = {'System_Id': systemId, 'Device_Id': deviceId, 'Sensor_Id': sensorId, 'Value': valueInt,
                     'BIT0': int(bitstr[31]), 'BIT1': int(bitstr[30]), 'BIT2': int(bitstr[29]), 'BIT3': int(bitstr[28]),
                     'BIT4': int(bitstr[27]), 'BIT5': int(bitstr[26]), 'BIT6': int(bitstr[25]), 'BIT7': int(bitstr[24]),
                     'BIT8': int(bitstr[23]), 'BIT9': int(bitstr[22]), 'BIT10': int(bitstr[21]),
                     'BIT11': int(bitstr[20]),
                     'BIT12': int(bitstr[19]), 'BIT13': int(bitstr[18]), 'BIT14': int(bitstr[17]),
                     'BIT15': int(bitstr[16]),
                     'BIT16': int(bitstr[15]), 'BIT17': int(bitstr[14]), 'BIT18': int(bitstr[13]),
                     'BIT19': int(bitstr[12]),
                     'BIT20': int(bitstr[11]), 'BIT21': int(bitstr[10]), 'BIT22': int(bitstr[9]),
                     'BIT23': int(bitstr[8]),
                     'BIT24': int(bitstr[7]), 'BIT25': int(bitstr[6]), 'BIT26': int(bitstr[5]), 'BIT27': int(bitstr[4]),
                     'BIT28': int(bitstr[3]), 'BIT29': int(bitstr[2]), 'BIT30': int(bitstr[1]),
                     'BIT31': int(bitstr[31])}
                lst.append({'channel': 'SensorRealtimeState', 'message': json.dumps(d)})
            else:
                d = {'System_Id': systemId, 'Device_Id': deviceId, 'Sensor_Id': sensorId, 'Value': "%.2f" % value}
                lst.append({'channel': 'SensorRealtimeData', 'message': json.dumps(d)})
        return lst
