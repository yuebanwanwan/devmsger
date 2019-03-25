#!/usr/bin/env python
#encoding=utf-8

'''
Created on 2016-03-26
@author: cdhongsheng.com
'''

class ParserNegotiation(object):
    def select_parser(self, frameHead, cmd_type, parsers):
        for parser in parsers:
            if frameHead == parser.frameHead and cmd_type == parser.cmd_type:
                return parser()
        return None