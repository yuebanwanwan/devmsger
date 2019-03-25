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
    hexArr = ['DF', '00', '08', '04', 'D2', '01']
    intArr = []

    for h in hexArr:
        intArr.append(int(h, 16))
    # print hex(crc16(intArr))

    print get_crc16('7E7E55320109000604D23601AB160570010066180427080947F1F132010900065AF0F01804270809F3F3FFD8FFE10FFE45786966000049492A0008000000050012010300010000000100000032010200140000004A0000000F010200400000005E00000010010200400000009E0000006987040001000000DE000000C8ABF0AB323031362D31312D323800000000000000000000C9D0F6CEBABDB5E7D7D3BFC6BCBCD3D0CFDEB9ABCBBE0000000000000000000000000000000000000000000000000000000000000000000000000000000000007378682D4C35000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000C009A82050001000000740100009D820500010000007C01000027880300010000006400000001920A00010000008401000003920A00010000008C01000004920A0001000000940100000792030001000000000000000992030001000000000000000A920500010000009C01000002A40300010000000000000003A40300010000000000000004A4050001000000A40100000000000005000000E8030000160000000A0000170BCF')

