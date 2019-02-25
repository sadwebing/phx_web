#-_- coding: utf-8 -_-

import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%d/%b/%Y:%H:%M:%S',
                filename='logs/access.log',
                filemode='a')

#配置文件
#bind = "0.0.0.0:8000"

#开发模式
reload = False

workers = multiprocessing.cpu_count() * 2 + 1    #进程数
threads = 4 #指定每个进程开启的线程数

accesslog = "./logs/access.log"
#access_log_format = ""
loglevel = "info"


