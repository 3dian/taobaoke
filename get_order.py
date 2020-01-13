#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/8 1:01 上午
# @Author  : Tang Jiuyang
# @Site    : https://tangjiuyang.com
# @File    : get_order_1min.py
# @Software: PyCharm
import requests
import configparser
import json
import pymysql
import sys
import datetime
import time
import os
from operator import itemgetter  # itemgetter用来去dict中的key，省去了使用lambda函数
from itertools import groupby  # itertool还包含有其他很多函数，比如将多个list联合起来。。
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

base_dir = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read("/root/www/taobaoke/config.ini")
ztkappkey = config['wechat']['ztkappkey']
pay_pass = config['wechat']['paypassowrd']
mysql_pass = config['mysql']['password']
sid = config['wechat']['sid']
qqmail_key = config['QQmail']['key']


def get_orders(start_time, end_time, get_tk_status='0'):
    url = 'https://api.zhetaoke.com:10001/api/open_dingdanchaxun2.ashx'
    payload = dict()
    payload['appkey'] = ztkappkey
    payload['sid'] = sid
    payload['start_time'] = start_time
    payload['end_time'] = end_time
    payload['query_type'] = '2'
    payload['page_size'] = '100'
    payload['jump_type'] = '1'
    payload['page_no'] = '1'
    payload['order_scene'] = '1'
    payload['signurl'] = 1

    if get_tk_status != '0':
        payload['tk_status'] = get_tk_status
    next_page = True
    # 打开数据库连接
    db = pymysql.connect("127.0.0.1", "root", mysql_pass, "taobaoke")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    while next_page is True:
        top_url = requests.get(url, params=payload)
        top_url_json = json.loads(top_url.text)
        res = requests.get(top_url_json['url'])
        res_json = json.loads(res.text)
        data = res_json['tbk_sc_order_details_get_response']['data']
        next_page = data['has_next']
        get_one_page(data, cursor, db)
        payload['position_index'] = data['position_index']
        payload['page_no'] = str(int(payload['page_no']) + 1)
    db.close()


def get_one_page(data, cursor, db):
    results = data['results']
    try:
        results['publisher_order_dto']
    except KeyError:
        return
    for result in results['publisher_order_dto']:
        order_id = result['trade_parent_id']
        item_title = result['item_title']
        item_num = result['item_num']
        tb_paid_time = result['tb_paid_time']
        order_id_6 = order_id[-6:]
        pub_share_pre_fee = result['pub_share_pre_fee']
        total_commission_fee = result['total_commission_fee']
        tk_status = result['tk_status']
        # 查询订单是否存在
        update_sql = "UPDATE wechat_orders SET pub_share_pre_fee='%s', total_commission_fee='%s', tk_status='%s' WHERE order_id='%s'" % (
            pub_share_pre_fee, total_commission_fee, tk_status, order_id)
        insert_sql = "INSERT INTO wechat_orders(order_id, item_title, item_num, " \
                     "tb_paid_time, order_id_6, pub_share_pre_fee, total_commission_fee, " \
                     "tk_status) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                         order_id, item_title, item_num, tb_paid_time,
                         order_id_6,
                         pub_share_pre_fee,
                         total_commission_fee, tk_status)

        sql = 'select openid, alipay, name from wechat_orders where order_id_6=%s ' \
              'and alipay IS NOT NULL and name IS NOT NULL and openid IS NOT NULL;' % (
                  order_id_6)
        try:
            # 执行sql语句
            find_user_info_res = cursor.execute(sql)
            if find_user_info_res > 0:
                a = cursor.fetchone()
                openid, alipay, name = a
                insert_sql = "INSERT INTO wechat_orders(openid, order_id, item_title, item_num, " \
                             "tb_paid_time, order_id_6, pub_share_pre_fee, total_commission_fee, " \
                             "tk_status,alipay, name) VALUES('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s')" % (
                                 openid, order_id, item_title, item_num,
                                 tb_paid_time,
                                 order_id_6,
                                 pub_share_pre_fee,
                                 total_commission_fee, tk_status, alipay, name)
            update_res = cursor.execute(update_sql)
            if update_res > 0:
                # 执行sql语句
                db.commit()
            else:
                cursor.execute(insert_sql)
                db.commit()
        except Exception as e:
            print(e)
            # 发生错误时回滚
            db.rollback()


def send_mail(email, date, mail_content):
    # qq邮箱smtp服务器
    host_server = 'smtp.qq.com'
    # sender_qq为发件人的qq号码
    sender_qq = '56312233'
    # pwd为qq邮箱的授权码
    pwd = qqmail_key
    # 发件人的邮箱
    sender_qq_mail = '56312233@qq.com'
    # 收件人邮箱
    receiver = email
    # 邮件的正文内容
    # mail_content = '你好，我是来自知乎的[邓旭东HIT] ，现在在进行一项用python登录qq邮箱发邮件的测试'
    # 邮件标题
    mail_title = date + '我要领券省钱结算明细'

    # ssl登录
    smtp = SMTP_SSL(host_server)
    # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
    smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)

    msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver
    smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
    smtp.quit()


def pay(alipay, name, amount):
    url = 'https://api.zhetaoke.com:10001/api/open_agent_alipay_money.ashx'
    if float(amount) < 0.1:
        amount = '0.1'
    params = {
        "appkey": ztkappkey,
        "password": pay_pass,
        "alipay_account": alipay,
        "alipay_name": name,
        "money": amount,
        "remark": "我要领券省钱返利结算"
    }
    res = requests.get(url, params)
    res_json = json.loads(res.text)
    if res.status_code == 200 and \
            res_json['alipay_fund_trans_toaccount_transfer_response'][
                'msg'] == 'Success' and \
            res_json['alipay_fund_trans_toaccount_transfer_response'][
                'pay_date'] != '':
        order_id = res_json['alipay_fund_trans_toaccount_transfer_response'][
            'order_id']
        good_url = "https://api.zhetaoke.com:10001/api/open_agent_alipay_money_list.ashx"
        good_params = {
            "appkey": ztkappkey,
            "password": pay_pass,
            "order_id": order_id,
        }
        good_res = requests.get(good_url, good_params)
        good_json = json.loads(good_res.text)
        if good_res.status_code == 200 and good_json['content'][0][
            'state'] == '1':
            return 'paid'


def settle_up():
    # 打开数据库连接
    db = pymysql.connect("127.0.0.1", "root", mysql_pass, "taobaoke")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor(pymysql.cursors.DictCursor)
    test_sql = 'select openid, pub_share_pre_fee, alipay, name from wechat_orders where tk_status=%s ' \
               'and alipay <>'' and name <>'' and openid <>'' AND settle_up IS NULL;' % (
                   '12')

    sql = "select item_title, order_id, item_num, tb_paid_time, total_commission_fee, alipay, name from wechat_orders where " \
          "tk_status='3' and alipay <>'' and name <>'' and openid <>'' AND settle_up IS NULL;"

    nopay_num = cursor.execute(sql)
    if nopay_num > 0:
        no_pay = cursor.fetchall()
        no_pay.sort(key=itemgetter('alipay'))  # 需要先排序，然后才能groupby。lst排序后自身被改变
        lstg = groupby(no_pay, itemgetter('alipay'))
        nopay_list = dict([(key, list(group)) for key, group in lstg])
        for k, v in nopay_list.items():
            alipay = k
            mail_content = ""
            for d in v:
                amount = round(float(d['total_commission_fee']) / 2, 2)
                # 调用api发钱
                status = pay(alipay, d['name'], str(amount))
                if status == 'paid':
                    update_sql = "UPDATE wechat_orders SET settle_up='yes' where order_id='%s';" % (
                    d['order_id'])
                    cursor.execute(update_sql)
                    db.commit()
                # 发送结算明细
                if '@' in alipay:
                    mail_content += f"商品标题: {d['item_title']}\n订单号: {d['order_id']}\n商品数量: {d['item_num']}\n付款时间: {d['tb_paid_time']}\n返利金额: {round(float(d['total_commission_fee']) / 2, 2)}\n===========================\n"
            send_mail(alipay,
                      datetime.datetime.today().strftime('%Y年%m月%d日'),
                      mail_content)


if __name__ == '__main__':
    # get_orders('2020-01-07 23:00:00', '2020-01-08 00:00:00')
    # pay('yszar@vip.qq.com', '唐九阳', '0.01')
    if sys.argv[1] == 'min':
        start_time = (datetime.datetime.now() - datetime.timedelta(
            minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        get_orders(start_time, end_time)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
              '订单查询成功!')
    if sys.argv[1] == 'day':
        start_time = (datetime.datetime.today() - datetime.timedelta(
            days=1)).strftime("%Y-%m-%d 00:00:00")
        for i in range(72):
            end_time = (datetime.datetime.strptime(start_time,
                                                   '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
                minutes=-19)).strftime("%Y-%m-%d %H:%M:%S")
            get_orders(start_time, end_time)
            start_time = (datetime.datetime.strptime(end_time,
                                                     "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
                minutes=-1)).strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(10)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
              (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(
                  "%Y-%m-%d"), '订单查询成功!')
    if sys.argv[1] == 'mon':
        start_time = (datetime.datetime.today() - datetime.timedelta(
            days=30)).strftime("%Y-%m-20 00:00:00")
        end_time = (datetime.datetime.strptime(start_time,
                                               '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
            minutes=-19)).strftime("%Y-%m-%d %H:%M:%S")
        while end_time[:10] != datetime.datetime.today().strftime('%Y-%m-%d'):
            get_orders(start_time, end_time, get_tk_status='3')
            start_time = (datetime.datetime.strptime(end_time,
                                                     "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
                minutes=-1)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = (datetime.datetime.strptime(start_time,
                                                   '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
                minutes=-19)).strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(5)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), (
                datetime.datetime.today() - datetime.timedelta(
            days=30)).strftime("%Y-%m"), '已结算订单查询成功!')
