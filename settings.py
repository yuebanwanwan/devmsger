#!/usr/bin/env python
# encoding=utf-8

'''
Created on 2016-3-26
@author: cdhongsheng.com
'''

from __future__ import unicode_literals

DEFAULTS = {
    'DEDIS_HOST': '127.0.0.1',
    'DEDIS_PORT': 6379,
    'DEVICE_SOFT_HOST': '127.0.0.1',
    'DEVICE_SOFT_PORT': 5005,
    'PHOTO_SOFT_HOST': '116.230.245.212',
    # 'PHOTO_SOFT_HOST': '192.168.102.217',
    # 'PHOTO_SOFT_PORT': 5008,
    'PHOTO_SOFT_PORT': 8090,
    'HEARTBEAT': 5,

}


class DevMsgerSettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from wechat.sdk.settings import api_settings
        print(api_settings.TOKEN)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = {}
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val


api_settings = DevMsgerSettings(None, DEFAULTS)


def reload_api_settings(*args, **kwargs):
    global api_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'DEVMSGER':
        api_settings = DevMsgerSettings(value, DEFAULTS)
