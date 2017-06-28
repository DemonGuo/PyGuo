#!/bin/bash
echo ===StartTime: $(date +%T)
echo [设环境变量HOST_ADDRESS PICP_PORT生效]
source ~/.bash_profile

echo [启动PICP挡板, 地址 $HOST_ADDRESS, 端口 $PICP_PORT ]
python TCPServer.py &
picp_pid=$(ps -ef|grep TCPServer.py|grep -v grep|wc -l)
echo 启动的进程数： $picp_pid
if [ $picp_pid != 0 ]
then
	echo 身份核查挡板启动成功, 日志文件picp.log, 配置文件id_config.cfg
else
	echo 身份核查挡板启动失败, 请查看日志文件picp.log
fi
echo ===EndTime: $(date +%T)
