# coding: utf-8

import socket
import threading

import time, random


class Test(object):

    def classify_stations(self, data_list, stations):
        """
        @param data_list: 包含所有站点的包
        @param stations: 包含所有站点信息的list
        @return: 分好类的dict, key为站点的name
        """
        stations = {k['telemetry_station'] + k['central_station']: k['name'] for k in stations}
        ret = {}
        for i in data_list:
            telemetry_station = i[6:16]
            central_station = i[4:6]
            station_address = telemetry_station + central_station
            # 根据遥测站和中心站地址获取站点名称
            station = stations[station_address]
            if station not in ret:
                ret[station] = []
                ret[station].append(i)
            else:
                ret[station].append(i)
        return ret


if __name__ == '__main__':
    t = Test()
    t.classify_stations()


