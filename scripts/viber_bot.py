#!/usr/bin/env python
#-_- coding:utf-8 -_-

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

import os
import logging

#获取当前目录
current_dir = os.path.abspath(os.path.dirname(__file__))

# 日志
logging.basicConfig(level=logging.INFO, filename="%s/logs/viber_bot.log" %current_dir, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot_configuration = BotConfiguration(
	name='saMonitorBot',
	avatar='http://viber.com/avatar.jpg',
	auth_token='4a73d9dc1127d3a1-bdfac7760afa25ea-6cfb6ca1663b11eb'
)
viber = Api(bot_configuration)

logger.info(viber.get_account_info())

viber.send_messages('1111', [
            "Hello World!"
        ])


# viber.set_webhook('https://www.baidu.com')

# 导入viber 信息模块
from viberbot.api.messages import (
    TextMessage,
    ContactMessage,
    PictureMessage,
    VideoMessage
)
from viberbot.api.messages.data_types.contact import Contact


text_message = TextMessage(text="Hello, World!")