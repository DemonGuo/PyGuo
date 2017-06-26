#!/bin/bash
echo ===StartTime: $(date +%T)
ps -ef|grep TCPServer.py|grep -v grep|awk '{print $2}'|xargs kill -9 2>&1

if [ $? -eq 0 ]
then
	echo 身份核查挡板停止成功。
else
	echo 身份核查挡板停止失败。
fi
echo ===EndTime: $(date +%T)

