#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time         = 2016/9/29 22:19
# @Author       = Demon
# @File         = TCPServer.py
# @Software     = PyCharm Community Edition
# @Description  =
import base64
import codecs
from configparser import ConfigParser
import sys

import time
from imp import reload

charset = 'utf8'
import os
from socketserver import TCPServer, BaseRequestHandler, StreamRequestHandler
import traceback
import logging
from xml.etree import ElementTree

global m_time
m_time = ""


class MyBaseRequestHandlerr(StreamRequestHandler):
    reqMsgTypeLen = 2
    reqLen = 1024

    def handle(self):
        logging.debug('客户端地址: %s', self.client_address)
        idConf = {}
        getIdConf(idConf)
        displayIdConf(idConf, False)

        while True:
            try:
                msgType = self.request.recv(self.reqMsgTypeLen).strip()
                logging.debug('[请求] 报文类型: %s', msgType)

                reqData = self.receive()
                logging.debug('[请求] 报文: %s', reqData.decode('gbk'))
                dXml = parseStrXml(reqData)

                sSRC = dXml['HEAD'].get('SRC', '')
                sMsgID = dXml['HEAD'].get('MsgID', '')
                sMsgRef = dXml['HEAD'].get('MsgRef', '')
                sWorkDate = dXml['HEAD'].get('WorkDate', '')
                sReserve = dXml['HEAD'].get('Reserve', '')
                sEntrustDate = dXml['MSG'].get('EntrustDate')
                sIssueOffice = r'此项暂不返回核查结果'
                sName = dXml['MSG'].get('Name', '')
                sID = dXml['MSG'].get('ID', '')

                hasName = idConf.get(sID, '')
                if len(checkReqData(dXml)) > 0:
                    sCheckResult = '05'
                    sPhoto64 = ''
                    str_err = '[检查] 输入参数错误[%s]' % checkReqData(dXml)
                    sReserve = '[ESB挡板错误信息提示(人行无此返回)] ' + str_err
                    logging.error(str_err)
                elif hasName == sName:
                    filePhoto = os.getcwd() + '/photo/' + sID + '.bmp'
                    if os.path.isfile(filePhoto):
                        sPhoto = open(filePhoto, 'rb').read()
                        sPhoto64 = base64.b64encode(sPhoto)
                        sCheckResult = '00'
                        logging.info('[检查] 姓名[%s]一致, 存在照片[%s]', sName, sID + '.bmp')
                    else:
                        sPhoto64 = ''
                        sCheckResult = '01'
                        logging.info('[检查] 姓名[%s]一致, 不存在照片[%s]', sName, sID + '.bmp')
                elif hasName == '':
                    sPhoto64 = ''
                    sCheckResult = '03'
                    str_err = '[检查] 证件号码不存在[%s]' % sID
                    sReserve = '[ESB挡板错误信息提示(人行无此返回)] ' + str_err
                    logging.error(str_err)
                elif len(hasName) > 0:
                    sPhoto64 = ''
                    sCheckResult = '02'
                    str_err = '[检查] 证件号码存在, 姓名不符合'
                    sReserve = '[ESB挡板错误信息提示(人行无此返回)] ' + str_err
                    logging.error(str_err)
                else:
                    sPhoto64 = ''
                    sCheckResult = '04'
                    logging.error('[检查] 其他错误')

                # print content
                rspData = '00<?xml version="1.0" encoding="GBK"?>' \
                          '<CFX>' \
                          '<HEAD>' \
                          '<VER>1.0</VER>' \
                          '<SRC>%s</SRC>' \
                          '<DES>100000000000</DES>' \
                          '<APP>联网核查公民身份信息系统</APP>' \
                          '<MsgNo>0002</MsgNo>' \
                          '<MsgID>%s</MsgID>' \
                          '<MsgRef>%s</MsgRef>' \
                          '<WorkDate>%s</WorkDate>' \
                          '<Reserve>%s</Reserve>' \
                          '</HEAD>' \
                          '<MSG>' \
                          '<SingleCheckResultHead0002>' \
                          '<EntrustDate>%s</EntrustDate>' \
                          '</SingleCheckResultHead0002>' \
                          '<SingleCheckResultMessage0002>' \
                          '<CheckResult>%s</CheckResult>' \
                          '<IssueOffice>%s</IssueOffice>' \
                          '<Name>%s</Name>' \
                          '<ID>%s</ID>' \
                          '<Photo>%s</Photo>' \
                          '</SingleCheckResultMessage0002>' \
                          '</MSG>' \
                          '</CFX>' \
                          % (sSRC, sMsgID, sMsgRef, sWorkDate, sReserve, sEntrustDate,
                             sCheckResult, sIssueOffice, sName, sID, sPhoto64)

                logging.debug('[返回] 响应报文: %s', rspData)
                self.request.send(rspData.decode('utf-8').encode('gbk'))
                # reloadCheck()
                return
            except:
                traceback.print_exc()
                print("====================================================")
                break

    def receive(self):
        reqData = ''
        while True:
            line = self.request.recv(self.reqLen).strip()
            reqData += line
            if line.endswith('</CFX>'):
                break
        return reqData
        pass


def getIdConf(idConf):
    filename = 'id_config.cfg'
    logging.debug('[getIdConf] 获取配置文件内容: %s', filename)

    if not os.path.exists(filename):
        logging.error('[getIdConf] 配置文件(%s) 不存在.', filename)
        idConf = {}
        return

    pfile = codecs.open(filename, 'rb', "utf-8")
    for line in pfile:
        if line == None or ('=' not in line) or line.startswith('#') or (len(line.split('=')) < 2):
            continue
        id = (line.split('=')[0]).strip()
        name = (line.split('=')[1]).strip()
        idConf[id] = name
    pfile.close()
    return
    pass


def displayIdConf(idConf, d_flag):
    if d_flag:
        for key in idConf.keys():
            logging.info('[displayIdConf] id=%s, name=%s.', key, idConf[key])
    logging.info('[displayIdConf] TotalRow: %d', len(idConf.keys()))
    pass


def setLog():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s  %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename='picp.log',
                        filemode='a'
                        )
    pass


def parseStrXml(sXml):
    # tempXml = open('tmp.xml','w')
    # tempXml.write(sXml.encode('utf-8'))
    # tempXml.close()
    sXml = sXml.decode('gbk').encode('utf-8')
    sXml = sXml.replace('GBK', 'UTF-8')
    root = ElementTree.fromstring(sXml)
    # root = ElementTree.parse('tmp.xml')
    logging.debug('解析请求报文开始------------------')
    dXml = {'HEAD': {}, 'MSG': {}}
    headlist = ['VER', 'SRC', 'DES', 'APP', 'MsgNo', 'MsgID', 'MsgRef', 'WorkDate', 'Reserve']
    msglist = ['BankCode', 'EntrustDate', 'BusinessCode', 'UserCode', 'ID', 'Name']
    for w in headlist:
        dXml['HEAD'][w] = root.find('HEAD/' + w).text

    dXml['MSG']['BankCode'] = root.find('MSG/SingleCheckBusinessHead0001/BankCode').text
    dXml['MSG']['EntrustDate'] = root.find('MSG/SingleCheckBusinessHead0001/EntrustDate').text
    dXml['MSG']['BusinessCode'] = root.find('MSG/SingleCheckBusinessHead0001/BusinessCode').text
    dXml['MSG']['UserCode'] = root.find('MSG/SingleCheckBusinessHead0001/UserCode').text
    dXml['MSG']['ID'] = root.find('MSG/SingleCheckRequestMessage0001/ID').text
    dXml['MSG']['Name'] = root.find('MSG/SingleCheckRequestMessage0001/Name').text

    for w in headlist:
        logging.debug('HEAD/%s = %s', w, dXml['HEAD'][w])

    for w in msglist:
        logging.debug('MSG/%s = %s', w, dXml['MSG'][w])

    logging.debug('解析请求报文结束------------------')
    return dXml
    pass


def checkReqData(dXml):
    logging.debug('检查请求报文开始------------------')
    headlist = ['VER', 'SRC', 'DES', 'APP', 'MsgNo', 'MsgID', 'MsgRef', 'WorkDate', 'Reserve']
    # msglist = ['BankCode', 'EntrustDate', 'BusinessCode', 'UserCode', 'ID', 'Name']
    headcheck = ['1.0', None, '100000000000', None, '0001', None, None, None, None]
    str_err = ''
    for i in range(len(headlist)):
        if (None != headcheck[i]) and (dXml['HEAD'].get(headlist[i], '') != headcheck[i]):
            str_err += '[checkReqData] 字段 %s, 当前值为[%s], 需要值[%s].' % \
                       (headlist[i], dXml['HEAD'][headlist[i]], headcheck[i])
            # logging.error(str_err)

            # if '313345010019' != dXml['MSG'].get('BankCode', ''):
            # if len(dXml['MSG'].get('BankCode', 'None')) < 12:
            # str_err += '[checkReqData] 字段 %s, 当前值为[%s], 需要值[%s].' % \
            # ('BankCode', dXml['MSG'].get('BankCode', ''), '313345010019')
            # str_err += '[checkReqData] 字段 %s, 当前值为[%s], 需要长度[12].' % \
            # ('BankCode', dXml['MSG'].get('BankCode', ''))
            # logging.error(str_err)

    if dXml['MSG'].get('ID', 'None') == 'None':
        str_err += '[checkReqData] 字段 ID, 长度为0.'
        # logging.error(str_err)

    if dXml['MSG'].get('Name', 'None') == 'None':
        str_err += '[checkReqData] 字段 NAME, 长度为0.'
        # logging.error(str_err)

    if (len(str_err) > 0):
        logging.info('检查请求报文结束,检查结果[FALSE]------------------')
    else:
        logging.info('检查请求报文结束,检查结果[TRUE]-------------------')

    return str_err
    pass


def main():
    conf = ConfigParser()
    cfgfile = os.getcwd().replace('\\', '/') + '/picpserver.conf'
    conf.read(cfgfile)
    host = conf.get('base', 'host')
    port = int(conf.get('base', 'port'))
    # host = os.getenv('HOST_ADDRESS')
    # port = int(os.getenv('PICP_PORT'))
    # print 'host:', host, ' port:', port
    addr = (host, port)
    setLog()
    print(sys.getfilesystemencoding())
    # 启动PCIP监听程序
    logging.debug("====启动PCIP监听程序, 地址：%s, 端口：%s====", host, port)
    server = TCPServer(addr, StreamRequestHandler)
    server.serve_forever()
    pass


def demon():
    # make child process and the father exit
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as error:
        print("fork father process failed")
        sys.exit(1)

    # 创建新的会话，子进程成为会话的首进程
    os.setsid()
    # 修改工作目录的umask
    os.umask(0)
    # 创建孙子进程，而后子进程退出
    try:
        pid = os.fork()
        if pid > 0:
            print("Daemon PID %d" % pid)
            sys.exit(0)
    except OSError as error:
        print("fork sub child process failed")
        sys.exit(1)

    run()
    pass


def reloadCheck():
    conffile = cfgfile = os.getcwd().replace('\\', '/') + '/picpserver.conf'
    global m_time
    setLog()
    logging.info("old modify time:[%s]" % m_time)
    while True:
        print ("check reload %s" % time.time())
        if m_time != time.ctime(os.path.getmtime(conffile)):
            logging.info("modify picpserver configs at time:[%s]" % time.ctime(os.path.getmtime(conffile)))
            reload(main())
            m_time = time.ctime(os.path.getmtime(conffile))
            time.sleep(1)
    pass


if __name__ == '__main__':
    main()
    # threading._start_new_thread(main())
