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

    def help_msg(self):
        self.__dict['Content'] = """一、买前来查优惠券,可发送淘口令或链接.
二、付款后发订单号来查询状态.
三、收货后发【提现】领红包.

【陶宝规则】付款时用谁的链接打开进入付款，就是谁的业务；如果用红包，就是发红包方的业务。

【注意】券、减免、满减、陶金币、购物津贴、支付宝红包这些都可以用（用后红包会按比例少一点），唯有付款处的抵扣红包不要用，用了就变成发红包方的业务了，这里就没有红包了。抵扣红包可以用到无优惠或低价的商品。

付款后发来订单编号查红包额且记到您名下。

提现红包：确认收货1分钟后发来2个字【提现】

查询余额：发来一个字【查】

【老用户实时提现】陶宝里确认收货1分钟后即可提现。

【新用户】30元内直接提现，超出单及疑问单下月21号后提现。

大额红包请次月20号官方给出结算明细后，找客服提现。

刷单及店陶等违规的一经发现立即封号无红包。

同时买多件：要把购物车里相同的删掉，再来用咱们的囗令打开加购物车，并当时买，付款处不要勾选用红包。
订单编号：在手机陶宝--我的陶宝--我的订单--点你买的宝贝--下划一点右侧边上有个红色（复制），点一下复制发来即可查询。

红包增减：红包是根据您实际付款额按比例增减的，您付款双倍，红包就多成双倍了。如果用了其他减免后实际付款少了，红包也就少了。

关于退货：不喜欢的商品不要确认收货，直接申请退货，多数商品还有运费险给您。退货退款无红包。

陶宝打不开优惠信息时，请升级陶到最新版，再清一下手机内存。

https://51lqsq.com 浏览器打开查券网址，用这里的囗令链接下单，发来订单编号也有红包。

买买买是件很开心的事，用我们囗令直接正常购买的，我们公众号再加送个红包，其他情况和您在陶宝上直接买一样。

【注意】
1、优惠信息有时效性，用当天的。
2、陶宝查单有时会延时几分钟。

=====================
❗❗❗【最最重要】
复制我们当天的优惠信息去直接买，中途退出或又看了别的广告，要重新复制去下单(付款处不要用陶宝红包，用了就没咱们这里的红包了)。
"""

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
🧧预估返红包【{cash_back}】元
----------------------------
复制我打开👉淘寳👈领券购买
付款后1分钟发来订单号进行确认
收货后发来【提现】二字领取红包
----------------------------
❗付款处不要用抵扣的红包，如果用了就没我们这里的红包了"""
        # 看详细介绍发来个？号。查券网 http://q.wycdym1008.xyz
        # tkl_dict = dict()
        # tkl_dict['ToUserName'] = ToUserName
        # tkl_dict['FromUserName'] = FromUserName
        # tkl_dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = msg_temp

        # return msg_temp

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
