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


def tkl_to_Content(ToUserName, FromUserName, old_tkl):
    urlcode_old_tkl = urllib.parse.quote(old_tkl, "utf-8")
    api_url = f'https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian_tkl.ashx?appkey={appkey}&sid=24661&pid=mm_26789644_290700478_80830800168&tkl={urlcode_old_tkl}&relation_id=&signurl=4'
    res = requests.get(api_url)
    res_json = json.loads(res.text)
    res_json = res_json['tbk_privilege_get_response']['result']['data']
    zk_final_price = int(res_json['zk_final_price']) - int(
        res_json['coupon_amount'])
    rebate_ratio = 0.5
    cash_back = zk_final_price * (
            float(res_json['max_commission_rate']) / 100) * rebate_ratio
    cash_back = round(cash_back, 1)

    msg_temp = f"""{res_json['title']}({res_json['tkl']})
领劵【{res_json['coupon_amount']}】
劵后【{zk_final_price}】
-------------------
现在复制本信息去购买
买后订单编号发来确认
收货后发来【提现】2字
返红包【{cash_back}】
-------------------
★付款处不要用抵扣的红包，如果用了就没我们这里的红包了
    """
    # 看详细介绍发来个？号。查券网 http://q.wycdym1008.xyz
    tkl_dict = dict()
    tkl_dict['ToUserName'] = ToUserName
    tkl_dict['FromUserName'] = FromUserName
    tkl_dict['CreateTime'] = int(time.time())
    tkl_dict['Content'] = msg_temp
    xmlForm = """
    <xml>
    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{Content}]]></Content>
    </xml>
    """
    return msg_temp


if __name__ == '__main__':
    image_identification(
        'http://mmbiz.qpic.cn/mmbiz_jpg/6zhPoZqUicsPIoRerYYKP6VexQTSeDwOmLcdTApHFupllKiaac5W9IictCEreEN3enGSotsdKnSwp5tZ8GW9j1RZA/0')
