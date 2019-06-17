#-_- coding: utf-8 -_-
from django.conf.urls import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url('get_domains$', views.GetDomains, name='GetDomains'),
    url('send_telegram$', views.SendTelegram, name='SendTelegram'),
    url('get_at_users$', views.getAtUsers, name='getAtUsers'),
    #url('get_telegram_user_id$', views.GetTelegramUserId, name='GetTelegramUserId'),

    # 发送telegram信息
    url('telegram$', views.TelegramGroup, name='TelegramGroup'),
    url('telegram/sendgroupmessage$', views.Telegramsendgroupmessage, name='Telegramsendgroupmessage'),
    url('telegram/uploadimgs$', views.TelegramUploadimgs, name='TelegramUploadimgs'),
]
