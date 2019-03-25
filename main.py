#!/usr/bin/env python
# encoding=utf-8

# http://www.cnblogs.com/gala/archive/2011/09/22/2184801.html #Python使用struct处理二进制
# http://www.cnblogs.com/coser/archive/2011/12/17/2291160.html

import time
from web.hsredis import HSRedis
from web.devheartbeat import DevHeartbeat
from dev.devsocket import DevSocket
# from dev.photosocket import PhotoSocket
from dev.my_photosocket import PhotoSocket

from pyfiglet import Figlet


def main():
    time.sleep(2)

    photosocket = PhotoSocket()
    photosocket.listen()

    # photosocket.send('7E7E32010900065F04D23680080200001804041606070566CA')

    """
    devsocket = DevSocket()
    devsocket.listen()

    hsredis = HSRedis(devsocket)
    hsredis.listen()

    devHeartbeat = DevHeartbeat()
    devHeartbeat.start()
    """


if __name__ == '__main__':
    f = Figlet(font='small')
    print f.renderText('devmsger')
    print u''
    print u'设备通信信使软件，该软件是中间件与采集软件的桥梁，请务必保证此软件处于正常运行状态。'
    print u'-------------------------------------------------------'
    print u'长沙国水信息科技有限公司  www.gocui.com.cn '
    print u'-------------------------------------------------------'
    print u''
    print u'运行日志：'
    main()
    raw_input('>>>>>>')
