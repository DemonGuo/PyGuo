#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time         = 2017/4/1 11:22
# @Author       = Demon
# @File         = view.py
# @Software     = PyCharm
# @Description  = 
import os
from encodings.utf_8 import encode
import sys

import logging
from django.shortcuts import render_to_response, render

reload(sys)
charset = 'utf8'
sys.setdefaultencoding(charset)

from django.http import HttpResponse

def setLog():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s  %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename='log_picp.log',
                        filemode='w',
                        encode='gb2312'
                        )
    pass

def addPicp(request):
    logging.debug('start the server')
    request.encoding = 'utf-8'
    info = 'input'
    ctx=''
    msg=''
    rlt = {}
    if info in request.GET:
        ctx=request.GET[info].encode('utf-8')
    else:
	str_err = '提交的内容为空'
	logging.error(str_err)
        return render_to_response('index.html', rlt)
	 
    filename = os.getcwd().replace('\\', '/') + '/PICPServerNew/id_config.cfg'
    logging.debug('cfg file full path:%s', filename)
    if not os.path.isfile(filename):
        str_err = '配置文件不存在：%s' % filename
        rlt['result'] = '添加身份证挡板信息失败, 失败原因:'
        rlt['msg'] = str_err
        logging.error(str_err)
        return render_to_response('picp.html', rlt)
        
    pfile = open(filename, 'a')
    d_id = ctx.split(',')
    for id in d_id:
        id=id.strip()
        if len(id) < 1:
            continue
        if '=' not in id:
            str_err = '[ 数据格式不正确, 缺少=号：%s]' % id
            msg += str_err
            logging.warn(str_err)
            continue
        pfile.write('\r\n'+id+'\r\n')
        msg += (id + ',')
        
    pfile.close()
    
    rlt['result'] = '添加身份证挡板信息:'
    rlt['msg'] = msg
    return render_to_response('picp.html', rlt)


def Picp_login(request):
    logging.debug('start picp web server...')
    return render_to_response('picp.html')
