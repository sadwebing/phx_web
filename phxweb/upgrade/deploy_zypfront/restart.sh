#!/bin/bash

config=config_dev.py

function restart {
port=$1
pid=$(ps -ef |grep gunicorn3 |grep -v grep |grep ${port} |awk '{print $2}' |sort |uniq |head -1)

echo "restarting port ${port}..."

while [ ! -z ${pid} ]
do
    kill -9 ${pid}
    echo "port ${port}: pid ${pid} killed..."
    pid=$(ps -ef |grep gunicorn3 |grep -v grep |grep ${port} |awk '{print $2}' |sort |uniq |head -1)
done

gunicorn3 -c ${config} -b 0.0.0.0:${port} gateway:app -D
sleep 3
pid=$(ps -ef |grep gunicorn3 |grep -v grep |grep ${port} |awk '{print $2}' |sort |uniq |head -1)
if [ ! -z ${pid} ];then
    echo "port ${port} restarted ok."
    ps -ef |grep gunicorn3 |grep -v grep |grep $port
else
    echo "port ${port} restarted failed. pls check!"
    ps -ef |grep gunicorn3 |grep -v grep |grep $port
fi
}

restart 8080
sleep 1
restart 8000
