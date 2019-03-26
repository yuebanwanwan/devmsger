#!/usr/bin/env python
# encoding=utf-8


import struct
import re


class Converter():

    @staticmethod
    def to_ascii(h):
        list_s = []
        for i in range(0,len(h),2):
            list_s.append(chr(int(h[i:i+2].upper(),16)))
        return ''.join(list_s)

    @staticmethod
    def to_hex(s):
        list_h = []
        for c in s:
            list_h.append(str(hex(ord(c)))[-2:]) #取hex转换16进制的后两位
        return ''.join(list_h)

    @staticmethod
    def hex_to_bytes(data):
        str2 = ''
        while data:
            str1 = data[0:2]
            print str1
            s = int(str1, 16)
            print s
            str2 += struct.pack('B', bytes(s))
            print str2
            data = data[2:]
        return str2

    @staticmethod
    def get_data_lst():
        """
        :return: data of list
        """
        res = ''
        with open('7305.txt', 'r') as f:
            global res
            res = f.read()
        pattern = re.compile(r'7e7e[\w]+')
        return re.findall(pattern, res)


if __name__ == '__main__':
    res = ''
    with open('7305.txt', 'r') as f:
        global res
        res = f.read()
    pattern = re.compile(r'7e7e[\w]+')
    for data in re.findall(pattern, res):
        print data
