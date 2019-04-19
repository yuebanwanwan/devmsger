#!/usr/bin/env python
#encoding=utf-8

import re

from web.my_crc import Crc16


def crc16(pchMsg):
    """
    # 十六进制，低位在前，高位在后，CRC_L+CRC_H,CRC16计算见CRC校验，CRC16是除CRC16字节外帧所有信息的CRC校验。
    # CRC校验是提高通信可靠性，防止帧数据流错误，该协议采用CRC16，参与CRC校验的对象除CRC本身外都参加校验。
    """
    wCRCTalbeAbs = [0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00,
                                0x2800, 0xE401, 0xA001, 0x6C00, 0x7800, 0xB401,
                                0x5000, 0x9C01, 0x8801, 0x4400]
    wCRC = 0xFFFF
    chChar = None
    
    wDataLen = len(pchMsg)
    for i in range(wDataLen):
        chChar = pchMsg[i]
        wCRC = wCRCTalbeAbs[(chChar ^ wCRC) & 15] ^ (wCRC >> 4)
        wCRC = wCRCTalbeAbs[((chChar >> 4) ^ wCRC) & 15] ^ (wCRC >> 4)
    
    chChar = wCRC
    wCRC = _ushort(wCRC >> 8);
    wCRC += _ushort(chChar << 8);
    return wCRC
    
    """
    l = wCRC & 0xff
    h = (wCRC >> 8) & 0xff
    return h, l
    """
    
def _ushort(n):
    return n & 0xffff


def cut_text(text,lenth):
    textArr = re.findall('.{'+str(lenth)+'}', text)
    textArr.append(text[(len(textArr)*lenth):])
    return textArr


def get_crc16(text):
    """根据报文生产crc16校验码并一起返回(校验码的高位字节与地位字节互换)
    text: 原始报文
    """
    hexArr = cut_text(text, 2)
    intArr = []
    for h in hexArr:
        if h != '':
            intArr.append(int(h, 16))
    crc = hex(crc16(intArr))
    if len(crc) == 5:
        r_crc = crc[3:5] + '0' + crc[2]
    else:
        r_crc = crc[4:6] + crc[2:4]
    return text + r_crc


def get_int_array(text):
    """根据十六进制字符串返回十进制整数数组
    """
    hexArr = cut_text(text, 2)
    intArr = []
    for h in hexArr:
        if h != '':
            intArr.append(int(h, 16))
    return intArr


if __name__ == '__main__':
    res = get_crc16('7E7E001000047316000036800802000119041613052605')
    print res
