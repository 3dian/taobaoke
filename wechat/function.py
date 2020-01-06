#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/2 5:44 下午
# @Author  : Tang Jiuyang
# @Site    : https://tangjiuyang.com
# @File    : function.py
# @Software: PyCharm
import urllib
import requests
import json
import time
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import \
    TencentCloudSDKException
from tencentcloud.tiia.v20190529 import tiia_client, models
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")
appkey = config['wechat']['ztkappkey']
tc_id = config['tencentcloud']['id']
tc_key = config['tencentcloud']['key']


def image_identification(img_url):
    cred = credential.Credential(tc_id, tc_key)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tiia.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tiia_client.TiiaClient(cred, "ap-beijing", clientProfile)

    req = models.DetectProductRequest()
    params = f'{{"ImageUrl": {img_url}}}'
    req.from_json_string(params)

    resp = client.DetectProduct(req)
    print(resp.to_json_string())


if __name__ == '__main__':
    image_identification(
        'http://mmbiz.qpic.cn/mmbiz_jpg/6zhPoZqUicsPIoRerYYKP6VexQTSeDwOmLcdTApHFupllKiaac5W9IictCEreEN3enGSotsdKnSwp5tZ8GW9j1RZA/0')
