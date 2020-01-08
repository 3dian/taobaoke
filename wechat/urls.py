#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/2 2:59 下午
# @Author  : Tang Jiuyang
# @Site    : https://tangjiuyang.com
# @File    : urls.py
# @Software: PyCharm
from django.urls import path
from .views import check_signature, wechat_js_mpxxx

urlpatterns = [
    path('', check_signature, name='wechat'),
    path('MP_verify_66hqUSGbYdBXbfKc.txt', wechat_js_mpxxx, name='wechat_js'),
]