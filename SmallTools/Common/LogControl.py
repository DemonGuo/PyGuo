#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time         = 2017/7/1 9:39
# @Author       = Demon
# @File         = LogControl.py
# @Software     = PyCharm
# @Description  = 

import logging
import os
import configparser


def GetLogger(logconf=None, logitem=None):
    """设置 logger 返回 log"""
    if None == logconf or '' == logconf.strip() or os.path.exists(logconf) or None == logitem or '' == logitem.strip():
        logconf = os.getcwd().replace('\\', '/') + '/Common/default.conf'
        logitem = 'default02'

    logging.config.fileConfig(logconf)
    logger = logging.getLogger(logitem)

    return logger


def SetLogger(logconf, logSection):
    if None == logconf or '' == logconf.strip():
        print("[SetLogger] input logconf is empty.")
        return
    conf = configparser.ConfigParser()

    if logSection not in conf.sections():
        print("[SetLogger] has not logSection[%s]." % logSection)

    level = int(conf.get(logSection, 'log_level'))
    fmtstr = conf.get(logSection, 'log_formatter').strip()
    formatter = logging.Formatter(fmtstr)
    datefmt = conf.get(logSection, 'log_datefmt').strip()
    logfile = conf.get(logSection, 'log_file').strip()
    maxbytes = int(conf.get(logSection, 'log_maxBytes'))
    count = int(conf.get(logSection, 'log_nums'))

    handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=maxbytes, backupCount=count)
    logging.basicConfig(level=level, format=formatter, datefmt=datefmt, filename=logfile, filemode='a', handlers=handler)

    logger = logging.getLogger(logfile[:logging.index('.')])
    return logger
    pass
