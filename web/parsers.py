#!/usr/bin/env python
# encoding=utf-8

'''
Created on 2016-3-26
@author: cdhongsheng.com
'''

import json
import struct
import binascii
import ctypes

from crc import crc16


class WebParser(object):
    """用于生产通过socket发送请求的二进制帧"""
    channel = None
    msg_tyep = 'message'
    cmd_type = '0x99'

    def parse(self, message):
        raise NotImplementedError(".parse() must be overridden.")

    def getfloatHex(self, float_value):
        """获取float的二进制"""
        s1 = struct.Struct('<f')
        prebuffer = ctypes.create_string_buffer(s1.size)
        s1.pack_into(prebuffer, 0, float_value)
        hexstr = binascii.hexlify(prebuffer)
        # print hexstr
        f8 = hexstr[:2]
        f16 = hexstr[2:4]
        f24 = hexstr[4:6]
        f32 = hexstr[6:8]

        """
        float_bytes = struct.pack('f', float_value)
        int_value = struct.unpack('l', float_bytes)[0]
        f8 = hex(int_value & 0xff)
        f16 = hex((int_value >> 8) & 0xff)
        f24 = hex((int_value >> 16) & 0xff)
        f32 = hex((int_value >> 24) & 0xff)
        """
        return f8, f16, f24, f32


class HeartbeatSocketParser(WebParser):
    """心跳包二进制帧"""
    channel = 'Heartbeat'
    cmd_type = '0x99'

    def parse(self, message):
        hexarr = ['DF', '00', '08', '00', '00', self.cmd_type]
        intarr = [int(item, 16) for item in hexarr]
        _crc = crc16(intarr)

        s1 = struct.Struct('!6B')
        s2 = struct.Struct('!H')
        prebuffer = ctypes.create_string_buffer(s1.size + s2.size)
        s1.pack_into(prebuffer, 0, *intarr)
        s2.pack_into(prebuffer, s1.size, _crc)
        # print binascii.hexlify(prebuffer)
        return prebuffer


class PhotoSocketParser(WebParser):
    """抓拍二进制帧"""
    channel = 'Photo'
    cmd_type = '0xaa'

    def parse(self, message):
        d = json.loads(message)
        user_id = d.get('User_Id', 0)
        system_id = d.get('System_Id', 0)
        device_id = d.get('Device_Id', 0)
        sensor_id = d.get('Sensor_Id', 0)
        sensor_expect_value = d.get('Sensor_Expect_Value', 0)

        f8, f16, f24, f32 = self.getfloatHex(sensor_expect_value)
        hexarr = ['DF', '00', '0f', hex((user_id >> 8) & 0xff), hex(user_id & 0xff), self.cmd_type, hex(
            system_id), hex(device_id), hex(sensor_id), f8, f16, f24, f32]
        intarr = [int(item, 16) for item in hexarr]
        _crc = crc16(intarr)

        s1 = struct.Struct('>13B')
        s2 = struct.Struct('>H')
        prebuffer = ctypes.create_string_buffer(s1.size + s2.size)
        s1.pack_into(prebuffer, 0, *intarr)
        s2.pack_into(prebuffer, s1.size, _crc)
        # print binascii.hexlify(prebuffer)
        return prebuffer


class RemoteExecutionSocketParser(WebParser):
    """远程操控二进制帧"""
    channel = 'RemoteExecution'
    cmd_type = '0xaa'

    def parse(self, message):
        d = json.loads(message)
        user_id = d.get('User_Id', 0)
        system_id = d.get('System_Id', 0)
        device_id = d.get('Device_Id', 0)
        sensor_id = d.get('Sensor_Id', 0)
        sensor_expect_value = d.get('Sensor_Expect_Value', 0)

        f8, f16, f24, f32 = self.getfloatHex(sensor_expect_value)
        hexarr = ['DF', '00', '0f', hex((user_id >> 8) & 0xff), hex(user_id & 0xff), self.cmd_type, hex(
            system_id), hex(device_id), hex(sensor_id), f8, f16, f24, f32]
        intarr = [int(item, 16) for item in hexarr]
        _crc = crc16(intarr)

        s1 = struct.Struct('>13B')
        s2 = struct.Struct('>H')
        prebuffer = ctypes.create_string_buffer(s1.size + s2.size)
        s1.pack_into(prebuffer, 0, *intarr)
        s2.pack_into(prebuffer, s1.size, _crc)
        # print binascii.hexlify(prebuffer)
        return prebuffer


class UndoRemoteExecutionSocketParser(RemoteExecutionSocketParser):
    """撤销远程操控二进制帧"""
    channel = 'UndoRemoteExecution'
    cmd_type = '0x55'
