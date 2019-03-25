#!/usr/bin/env python
#encoding=utf-8

'''
Created on 2016-03-26
@author: cdhongsheng.com
'''

class ParserNegotiation(object):
    def select_parser(self, channel, msg_type, parsers):
        for parser in parsers:
            if channel == parser.channel and msg_type == parser.msg_tyep:
                return parser()
        return None