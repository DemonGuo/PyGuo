import os
import sys

import logging
from django.shortcuts import render_to_response, render
charset = 'utf-8'
from django.http import HttpResponse


# def setLog():
#     logging.basicConfig(level=logging.DEBUG,
#                         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s  %(message)s',
#                         datefmt='%d %b %Y %H:%M:%S',
#                         filename='log_picp.log',
#                         filemode='w'
#                         )
#     pass


def addPicp(request):
    logging.debug('start the server')
    request.encoding = 'utf-8'
    info = 'input'
    ctx = ''
    msg = ''
    rlt = {}
    if info in request.GET:
        ctx = request.GET[info].encode('utf-8').decode()
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

    pfile = open(filename, 'a', encoding='utf-8')
    d_id = ctx.split(',')
    for id in d_id:
        id = id.strip()
        if len(id) < 1:
            continue
        if '=' not in id:
            str_err = '[ 数据格式不正确, 缺少=号：%s]' % id
            msg += str_err
            logging.warn(str_err)
            continue
        pfile.write('\r\n' + id)
        src_photo = os.getcwd().replace('\\', '/') + '/PICPServerNew/photo/1.bmp'
        idnum = id.split('=')[0]
        target_photo = os.getcwd().replace('\\', '/') + '/PICPServerNew/photo/%s.bmp' % idnum
        if not os.path.exists(target_photo) and os.path.isfile(src_photo) :
            open(target_photo, "wb").write(open(src_photo, "rb").read())
        msg += (id + ',')

    pfile.close()

    rlt['result'] = '添加身份证挡板信息: 添加照片成功'
    rlt['msg'] = msg
    return render_to_response('picp.html', rlt)


def Picp_login(request):
    logging.debug('start picp web server...')
    return render_to_response('picp.html')