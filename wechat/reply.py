#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/2 3:15 下午
# @Author  : Tang Jiuyang
# @Site    : https://tangjiuyang.com
# @File    : reply.py.py
# @Software: PyCharm
import json
import time
import urllib
import re
import requests
import configparser
from decimal import Decimal

config = configparser.ConfigParser()
config.read("./config.ini")
appkey = config['wechat']['ztkappkey']


class Msg(object):
    def __init__(self):
        pass

    def send(self):
        return 'success'


class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def tkl_to_json(self):
        urlcode_old_tkl = urllib.parse.quote(self.__dict['Content'], "utf-8")
        api_url = f'https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian_tkl.ashx?appkey={appkey}&sid=24661&pid=mm_26789644_290700478_80830800168&tkl={urlcode_old_tkl}&relation_id=&signurl=4'
        res = requests.get(api_url)
        return json.loads(res.text)

    def link_to_json(self):
        pair = re.compile(r'.*&id=(\d*).*')
        num_id = pair.match(self.__dict['Content']).group(1)
        api_url = f'https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian.ashx?appkey={appkey}&sid=24661&pid=mm_26789644_290700478_80830800168&num_iid={num_id}&me=&relation_id=&signurl=4'
        res = requests.get(api_url)
        return json.loads(res.text)

    def json_to_Content(self, res_json):
        res_json = res_json['tbk_privilege_get_response']['result']['data']
        print(res_json['zk_final_price'])
        print(res_json['coupon_amount'])
        print(res_json['max_commission_rate'])
        if res_json['coupon_amount'] == "":
            res_json['coupon_amount'] = 0
        zk_final_price = float(res_json['zk_final_price']) - float(
            res_json['coupon_amount'])
        rebate_ratio = 0.5
        cash_back = zk_final_price * (
                float(res_json['max_commission_rate']) / 100) * rebate_ratio
        # cash_back = round(cash_back, 2)
        cash_back = Decimal(str(cash_back)).quantize(Decimal('0.00'))

        msg_temp = f"""🌹~专属福利~🌹
【商品】{res_json['title']}
淘口令: {res_json['tkl']}
😁领劵【{res_json['coupon_amount']}】元
💰劵后【{zk_final_price}】元
🧧预估返还【{cash_back}】元
----------------------------
复制我打开👉淘寳👈领券购买
付款后1分钟发来订单号进行确认
收货后21号系统自动结算返还金额
----------------------------
❗新用户请务必绑定支付宝账户,否则无法收到返款,绑定方法请发送 h 进行查看.
❗付款处不要用抵扣的红包，如果用了就没我们这里的红包了"""
        # 看详细介绍发来个？号。查券网 http://q.wycdym1008.xyz
        # tkl_dict = dict()
        # tkl_dict['ToUserName'] = ToUserName
        # tkl_dict['FromUserName'] = FromUserName
        # tkl_dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = msg_temp

        # return msg_temp

    def order_to_Content(self, item_num, pub_share_pre_fee):
        order_msg = f"""亲，此订单共{item_num}件商品，已记入{pub_share_pre_fee}元，确认收货后21号可来提现祝您开心！[玫瑰]
------------------
提现：陶宝里确认收货之后的第一个21号,发来【提现】2字，这里就会自动发微信红包

查明细发来1个字：查
看详细介绍发英文 h"""
        self.__dict['Content'] = order_msg

    def settle_up_to_Content(self, total, titles):
        settle_up_msg = f"""未结算：【{total}】元
{titles}
-------------------
提现：陶宝里确认收货之后的第一个21号,发来【提现】2字，这里就会自动发微信红包

查明细发来1个字：查
看详细介绍发英文 h"""
        self.__dict['Content'] = settle_up_msg

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)


class ImageMsg(Msg):
    def __init__(self, toUserName, FromUserName, mediaId):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = FromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = mediaId

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        """
        return XmlForm.format(**self.__dict)


class VoiceMsg(Msg):
    def __init__(self, toUserName, FromUserName, mediaId):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = FromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = mediaId

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[voice]]></MsgType>
        <Voice>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Voice>
        </xml>
        """
        return XmlForm.format(**self.__dict)


class EventMsg(Msg):
    def __init__(self, toUserName, FromUserName, title, description, picurl,
                 url):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = FromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Title'] = title
        self.__dict['Description'] = description
        self.__dict['Picurl'] = picurl
        self.__dict['Url'] = url

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>1</ArticleCount>
        <Articles>
        <item>
        <Title><![CDATA[{Title}]]></Title>
        <Description><![CDATA[{Description}]]></Description>
        <PicUrl><![CDATA[{Picurl}]]></PicUrl>
        <Url><![CDATA[{Url}]]></Url>
        </item>
        </Articles>
        </xml>
        """
        return XmlForm.format(**self.__dict)
