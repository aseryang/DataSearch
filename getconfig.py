# -*- coding: utf-8 -*-

import configparser


def getConfig(section, key):
    config = configparser.ConfigParser()
    config.read('configs.conf')
    return config.get(section, key)
